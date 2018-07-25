# -*- coding: utf-8 -*-
import os

from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy.exc import IntegrityError

import zipfile
import uuid
import ipfsapi
import shutil

from ipfsapi.exceptions import ConnectionError
from models import Uploads

# What is allowed to be uploaded directly
ALLOWED_UPLOAD_EXTENSIONS = set(['zip', 'fbx', 'js', 'json'])
# What is allowed to be inside a zip file.
ALLOWED_CONTENT_EXTENSIONS = set(
    ['fbx', 'jpg', 'png', 'tga', 'fst', 'js', 'json'])
# Check

def allowed_file(filename, extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[-1].lower() in extensions or \
        filename.endswith("/")


def process(app, db, request, user):
    try:
        api = ipfsapi.connect('ipfs', 5001)
    except ConnectionError as e:
        return {'error': 'Could not establish connection to ipfs!'}

    if 'file' not in request.files:
        return {'error': 'No Selected File!'}

    file = request.files['file']

    if file.filename == '':
        return {'error': 'No Selected File!'}

    if not allowed_file(file.filename, ALLOWED_UPLOAD_EXTENSIONS):
        return {'error': 'File type not allowed!'}

    # This may actually need to be unpacked to save memory, but for now, for example purposes, its simple.
    response = None
    valid = True

    uuid_gen = uuid.uuid5(uuid.NAMESPACE_DNS, file.filename +
                          datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    unique_id = str(uuid_gen)

    directory = app.config['UPLOAD_FOLDER'] + unique_id + "/"
    if file.filename.rsplit('.', 1)[-1].lower() == 'zip':
        try:
            zf = zipfile.ZipFile(file, 'r')
            file_names = zf.namelist()
            err = []

            for file_name in file_names:
                valid = allowed_file(file_name, ALLOWED_CONTENT_EXTENSIONS)

                if not valid:
                    err.insert(file_name)

            if not valid:
                response = {
                    "error": "Following Files are not allowed", "details": err}
            else:

                for file_name in file_names:
                    # Do, not, extract empty directories.
                    if not file_name.endswith("/"):
                        zf.extract(file_name, directory)

                original_response = api.add(directory, recursive=True)

                response = []
                for item in original_response:
                    # Remove directory id name
                    if "Name" in item.keys():
                        item["Name"] = item["Name"].replace(unique_id, '')
                        if len(item["Name"]) is 0:
                            item["Name"] = file.filename

                    response.append(item)

                try:
                    for item in response:
                        print(item)
                        # Check that the hash already is not in the database for the user. This occurs with some files that might be shared between users.
                        if Uploads.query.filter_by(uploader=user.id, ipfs_hash=item["Hash"]).first() is None:
                            db.session.add(
                                Uploads(uploader=user.id, ipfs_hash=item["Hash"], original_name=item["Name"]))

                    db.session.commit()
                except IntegrityError as e:
                    print("Could not commit file, Already exists!", e)
        finally:
            zf.close()
            if directory is not None:
                shutil.rmtree(directory)

    return response
