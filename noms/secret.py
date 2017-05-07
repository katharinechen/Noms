"""
Passwords, intended to be stored in the database
"""
import os
import StringIO

import time

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


def fetchAWSConfig(): 
    """
    Fetch secret pairs from AWS config file and load it in mongo
    """
    # get the secret_pair.json file from AWS 
    s3 = boto3.resource('s3')
    loading_bucket = s3.buckets.filter(Name="config.{ph}".format(ph=CONFIG.public_hostname))
    if len(loading_bucket) > 0: 
        loading_bucket = loading_bucket[0]
    else: 
        loading_bucket = s3.Bucket("config.dev.nomsbook.com")
    output = StringIO.StringIO() 
    loading_bucket.download_fileobj('secret_pair/secret_pair.json', output)

    # save it to mongo if mongo is empty
    if SecretPair.objects.count() == 0: 
        SecretPair._get_collection().insert(json_util.loads(output.getvalue())) 