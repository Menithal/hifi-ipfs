from flask import request, jsonify, redirect, url_for
import secrets

from models import Credentials, pbdkdf2_hash_base64, Uploads

import file_upload

# Grassroots routes


def routes(app, db):
    def _authentication(username, token):
        if username is None:
            return None

        print("authenticated", username)
        user = Credentials.query.filter_by(
            username=username.lower()
        ).first()

        print('Got', user)
        if user is None or token is None:
            return None

        print("Token to use", token, user.salt)
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
        return 'Prototype IPFS with Web UI. Connect via Plugin.'

    @app.route('/routes', methods=['GET'])
    def routes():
        # This is used by external plugins to check for existing links.
        # Both should be GET and POST compatible, with POST being the submission, while GET is the public
        return jsonify({
            "new_user": "/new",
            "asset_upload": "/asset_upload",
            "uploads": "/uploads"
        })

    @app.route('/asset_upload', methods=['GET', 'POST'])
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

        return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <ul>
                <li><h2>Anything you upload to service via the blender plugin will be put onto the ipfs for everyone <strong>with the ipfs url</strong> to the file</h2></li>
                <li>You agree not to upload any Personal information onto this prototype site.</li>
                <li>Uploading <strong>you agree that you have rights to upload the materials you upload to the IPFS</strong> via this service</li>
            </ul>
            <form method=post enctype=multipart/form-data>
                <input type=file name=file> <br/>
                <input type=text placeholder="username" name=username> <br/>
                <input type=text placeholder="token" name=token><br/>
                <input type=submit value=Upload>
            </form>
        '''
    # TODO: File removal could be done after request instead of inside file_upload.process

    @app.route('/uploads', methods=['GET', 'POST'])
    def check_uploads():

        # TODO: If you want session service, use it herew
        if request.method == 'POST':
            user = _authentication(
                request.form['username'], request.form['token'])

            if user is None:
                return jsonify({'error': 'Could not authenticate with provided information.'})

            uploads = Uploads.query.filter_by(
                uploader=user.id
            )

            return jsonify(uploads)

        return '''
            <!doctype html>
                <title>Login</title>
                <h1> Check Available </h1>
                <li>This site uses no cookies to maintain your login, once you go off, you will be not be logged back in</li>
                   
                <form method=post>
                    <input type=text placeholder="username" name=username> <br/>
                    <input type=text placeholder="token" name=token><br/>
                    <input type=submit value="Check Uploads">
                </form>
        '''

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

        # TODO: Update to use Jinja2 with template files instead of this.
        return '''
            <!doctype html>
                <title>Quick and Dirty Credentials</title>
                <h1>Quick and Dirty Credentials: </h1>
                <h2>Notice:</h2>
                <ul>
                    <li>Do <strong>NOT</strong> use for production this is just for proof of concept. Which is why this only accepts a user name and it will generate a token for you. </li>
                    <li>All information is as anonymous as you make it with the username you want to use. </li>
                    <li><strong> Do not lose token or share it with anyone else</strong>,that is your access token.</li>
                    <li>After generating a token, you will not be able to recover or update it. </li>
                    <li>This site stores your login, generated here</li>
                    <li>This site stores the links to anything uploaded, which individuals with access tokens may access. </li>
                    <li>You may only upload files for the use on the High Fidelity platform. Only exception is html pages</li>
                    <li>You can only upload zip or fbx files into the services</li>
                    <li>If you upload a zip file, additional formats supported within the zip file are: fbx, tga, png, jpg, fbm, js, fst</li>
                    <li>Suggest method of upload, use the Blender plugin. Blender will generate the links</li>
                </ul>
                <h3>You agree to following:</h3>
                <h2>July 9 2018</h2>
                <ul>
                   <li><h2>Anything you upload to service via the blender plugin or this service will be put onto the ipfs <strong>Anyone with the ipfs url</strong> will be able to access the file</h2></li>
                   <li>You agree not to upload any Personal information onto this prototype site.</li>
                   <li>You agree <strong>that you have rights to upload the materials you upload to the IPFS</strong> via this service</li>
                   <li>Accept that this is just a relay service which does nothing with your data, but passing it on into the ipfs node network.</li>
                </ul>
                <p>When you Generating a key, you accept the above conditions</p>
                <form method=post>
                    <input type=text placeholder="username of choice" name=username>
                    <input type=submit value="I Agree and Generate">
                </form>
        '''
