# -*- coding: utf-8 -*-
from main import db
from sqlalchemy.sql import func
from sqlalchemy.schema import UniqueConstraint
import hashlib
import binascii

# DO NOT USE OUTSIDE OF PROTOTYPE


# TODO: Probabaly OpenSSL method would be better? for now use this-
def pbdkdf2_hash(token, salt):
    ha = hashlib.pbkdf2_hmac('sha512', token.encode(), salt.encode(), 1000)
    return ha.decode('ISO-8859-1') + '==='


def pbdkdf2_hash_base64(token, salt):
    return binascii.b2a_base64(
        (pbdkdf2_hash(token, salt)).encode()).decode('utf-8')


class Credentials(db.Model):
    __tablename__ = 'credentials'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    token_hash = db.Column(db.Text())
    salt = db.Column(db.Text())

    def __init__(self, username, token, salt):
        self.username = username.lower()
        self.salt = salt
        self.token_hash = pbdkdf2_hash_base64(token, salt)

    def __repr__(self):
        return '<Credential %r>' % self.username


# This entire part is optional
class Uploads(db.Model):
    __tablename__ = 'uploads'
    __table_args__ = tuple(UniqueConstraint(
        'uploader', 'ipfs_hash', name='uploader_ipfs_hash_unique_constraint'))

    id = db.Column(db.Integer, primary_key=True)
    uploader = db.Column(db.Integer, db.ForeignKey('credentials.id'))
    ipfs_hash = db.Column(db.Text())
    original_name = db.Column(db.Text())
    parent_hash = db.Column(db.Text())
    is_avatar = db.Column(db.Boolean(), default=False)
    date = db.Column(db.DateTime, server_default=func.now())
