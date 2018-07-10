# -*- coding: utf-8 -*-
from flask import request, jsonify, redirect, url_for
import secrets

from models import Credentials, pbdkdf2_hash_base64, Uploads
import file_upload

def routes(app, db, env):
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
        return 'Heimdall v0.01. Connect via Plugin.'

    @app.route('/plugin_routes', methods=['GET'])
    def routes():
        # This is used by external plugins to check for existing links.
        # Both should be GET and POST compatible, with POST being the submission, while GET is the public
        return jsonify({
            "new_user": "/new",
            "asset_upload": "/upload",
            "uploads": "/uploads"
        })

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            print(request.form)
            user = _authentication(
                request.form['username'], request.form['token'])

            if user is None:
                return jsonify({'error': 'Could not authenticate with provided information.'})

            try:
                return jsonify(file_upload.process(app, db, request, user))

            except Exception as e:
                return jsonify({'error': e})

        return env.get_template('uploader.html').render()

    # TODO: File removal could be done after request instead of inside file_upload.process

    @app.route('/uploads', methods=['GET', 'POST'])
    def check_uploads():

        if request.form['username'] and request.form['token']:
            user = _authentication(
                request.form['username'], request.form['token'])

            if user is None:
                return jsonify({'error': 'Could not authenticate with provided information.'})

            uploads = Uploads.query.filter_by(
                uploader=user.id
            )

            return env.get_template('uploads.html').render(uploads=uploads, username=user.username)

        return env.get_template('query.html').render()

    # TODO: Update when creating proper authentication channels.
    @app.route('/new', methods=['GET', 'POST'])
    def create_credentials():

        if request.method == 'POST':
            if len(request.form['username']) == 0:
                return redirect(url_for('create_credentials'))

            val = Credentials.query.filter_by(
                username=request.form['username']).first()

            if val is not None:
                return jsonify({'username': request.form['username'], 'error': 'Token already generated.'})

            secret = secrets.token_urlsafe()
            salt = secrets.token_urlsafe()

            user = Credentials(request.form['username'], secret, salt)

            db.session.add(user)
            db.session.commit()

            return jsonify({'username': request.form['username'], 'secret': secret, 'notes': 'DO NOT LOSE THIS'})

        return  env.get_template('new_user.html').render()
