"""
Passwords, intended to be stored in the database
"""
from __future__ import print_function

import os
import io

from bson import json_util  

import boto3 

from mongoengine import fields

from noms import documentutil, CONFIG


NO_DEFAULT = object()
SECRET_EXPIRATION = 600 # 10 minutes


class SecretPair(documentutil.NomsDocument):
    """
    A named password, auth token, or other secret with its public pair
    """
    name = fields.StringField(unique=True, required=True)
    public = fields.StringField()
    secret = fields.StringField(required=True)

    meta = {'indexes': ['name']}

    @classmethod
    def get(cls, name, default=NO_DEFAULT):
        ret = cls.objects(name=name
                ).only('public', 'secret'
                ).first()

        if ret is None:
            if default is NO_DEFAULT:
                raise KeyError(name)
            return default

        return ret.public.encode('ascii'), ret.secret.encode('ascii')

    @classmethod
    def put(cls, name, public, secret):
        return cls(name=name, public=public, secret=secret).save()


get = SecretPair.get

put = SecretPair.put


def randomPassword(n=32):
    """
    Produce a string n*2 bytes long, of hex digits
    """
    return ''.join('%02x' % ord(c) for c in os.urandom(n))


def loadFromS3(): 
    """
    Fetch secrets from config file held in S3, and load them in mongo

    If a bucket matching 'config.' + public_hostname exists, get secrets file
    from there. Otherwise, get them from config.dev.nomsbook.com

    Does nothing if the secret_pair collection already exists; to force, drop
    the secret_pair collection.
    """
    if SecretPair.objects.count() == 0: 
        # get the secret_pair.json file from AWS 
        s3 = boto3.resource('s3')
        for b in s3.buckets.all():
            if b.name == 'config.%s' % CONFIG.public_hostname:
                bucket = b
                break
        else:
            bucket = s3.Bucket("config.dev.nomsbook.com")

        output = io.StringIO() 
        bucket.download_fileobj('secret_pair/secret_pair.json', output)

        # save it to mongo
        print("Piping hot fresh secrets from bucket %r" % bucket.name)
        SecretPair._get_collection().insert(json_util.loads(output.getvalue())) 
