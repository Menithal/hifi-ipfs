
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
                directory = app.config['UPLOAD_FOLDER'] + unique_id + "/"

                for file_name in file_names:
                    # doing individuals to make sure nothing is relative.
                    zf.extract(file_name, directory)

                print("Uploading directory", directory)

                response = api.add(directory, recursive=True)

                print("IPFS Transfer Complete. Removing directory", directory)
                shutil.rmtree(directory)

                try:
                    # This part stores all the submissions
                    for item in response:
                        print(item)
                        print(user.id, item["Hash"], item["Name"])
                        db.session.add(
                            Uploads(uploader=user.id, ipfs_hash=item["Hash"], original_name=item["Name"].replace(unique_id)))

                    db.session.commit()
                except IntegrityError:
                    print("Could not commit, Probably already exists")

                print("Responding to client with new hashes.")

                return response
        finally:
            zf.close()

    return response
