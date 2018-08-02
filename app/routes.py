# -*- coding: utf-8 -*-
from flask import request, jsonify, redirect, url_for, session
import secrets

from models import Credentials, pbdkdf2_hash_base64, Uploads
import file_upload
import json

from http_client import oauth_connect


def routes(app, db, env):

    OAUTH_API = app.config["OAUTH_LOGIN_API"]

    def _authentication(username, token):
        if username is None:
            return None

        user = Credentials.query.filter_by(
            username=username.lower()
        ).first()

        if user is None or token is None:
            return None

        token_check = Credentials.query.filter_by(
            username=username.lower(),
            token_hash=pbdkdf2_hash_base64(
                token=token, salt=user.salt)
        ).first()

        if token_check is None:
            return None

        return user

    @app.route('/')
    def landing():
        return 'Heimdall v0.5. Connect via Plugin.'

    @app.route('/plugin_routes', methods=['GET'])
    def routes():
        # This is used by external plugins to check for existing links.
        # Both should be GET and POST compatible, with POST being the submission, while GET is the public
        available_config = {
            "oauth": app.config["OAUTH_ENABLED"] == '1',
            "new_user": "/new",
            "asset_upload": "/upload",
            "uploads": "/uploads"
        }

        if app.config["OAUTH_ENABLED"] == '1':
            available_config["oauth_link"] = app.config["OAUTH_TOKEN_LINK"] == '1'

        return jsonify(available_config)

    @app.route('/upload', methods=['POST'])
    def upload_file():

        user = _authentication(
            request.form['username'], request.form['token'])

        if user is None:
            return jsonify({'error': 'Could not authenticate with provided information.'})

        try:
            return jsonify(file_upload.process(app, db, request, user))

        except Exception as e:
            return jsonify({'error': e})

    # TODO: File removal could be done after request instead of inside file_upload.process

    @app.route('/uploads', methods=['GET', 'POST'])
    def check_uploads():
        if request.method == "POST":

            if request.form['username'] is not None:
                session['username'] = request.form['username']

            if request.form['token'] is not None:
                session['token'] = request.form['token']

            user = _authentication(session['username'], session['token'])

            if user is None:
                return jsonify({'error': 'Could not authenticate with provided information.'})

            uploads = Uploads.query.filter_by(
                uploader=user.id
            )

            if request.form['page'] != None:
                page = int(request.form['page'])
            else:
                page = 1

            return env.get_template('uploads.html').render(uploads=uploads, username=user.username, page=page)
        elif (request.args is not None and request.args.get('username') is not None and request.args.get('token') is not None) or (session is not None and "username" in session and 'token' in session):

            if request.args.get('username') is not None:
                session['username'] = request.args.get('username')

            if request.args.get('token') is not None:
                session['token'] = request.args.get('token')

            user = _authentication(session['username'], session['token'])

            if user is None:
                return jsonify({'error': 'Could not authenticate with provided information.'})

            uploads = Uploads.query.filter_by(
                uploader=user.id
            )

            if request.args.get('page') != None:
                page = int(request.args.get('page'))
            else:
                page = 1

            max_count = 25
            page_count = round(uploads.count() / max_count)

            return env.get_template('uploads.html').render(uploads=uploads, username=user.username, page=page, page_count=page_count, max_count=max_count)

        return ""

    # TODO: Update when creating proper authentication channels.
    @app.route('/new', methods=['POST'])
    def create_credentials():

        if not app.config["OAUTH_ENABLED"]:
            print("Request through non OAUTH")
            val = Credentials.query.filter_by(
                username=request.form['username']).first()

            if val is not None:
                db.session.close()
                return jsonify({'username': request.form['username'], 'error': 'Token already generated.'})

            secret = secrets.token_urlsafe()
            salt = secrets.token_urlsafe()

            user = Credentials(request.form['username'], secret, salt)

            db.session.add(user)
            db.session.commit()

            return jsonify({'username': request.form['username'], 'secret': secret, 'notes': 'DO NOT LOSE THIS'})
        else:
            # Now if the application has OAUTH_ENABLED, then we will actually check if the token returns the correct result back from the server.

            user = Credentials.query.filter_by(
                username=request.form['username']).first()

            result = json.loads(oauth_connect(
                OAUTH_API, request.form['oauth']))

            if len(request.form['oauth']) == 0:
                db.session.close()
                return jsonify({'error': 'Oauth token is required by the server.'})

            if "error" in result.keys():
                db.session.close()
                return jsonify({"error": "Oauth token was not valid: Service response:" + result['error']})

            try:
                if request.form["username"].lower() != result['data']['user']['username'].lower():
                    db.session.close()
                    return jsonify({"error": "Invalid Username token comparison."})
            except Exception as e:
                db.session.close()
                return jsonify({"error": "Invalid Username token comparison. Oauth server response was:" + str(e)})

            secret = secrets.token_urlsafe()
            salt = secrets.token_urlsafe()

            if user is None:
                new_user = Credentials(
                    request.form['username'].lower(), secret, salt)
                db.session.add(new_user)
            else:
                user.token_hash = pbdkdf2_hash_base64(secret, salt)
                user.salt = salt

            db.session.commit()

            return jsonify({'username': request.form['username'], 'secret': secret, 'notes': 'You may recreate the token with a valid oauth key later.'})

        return ""
