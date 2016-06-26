"""
Passwords, intended to be stored in the database
"""
from mongoengine import fields

from noms import documentutil


class SecretPair(documentutil.NomsDocument):
    """
    A named password, auth token, or other secret with its public pair
    """
    name = fields.StringField(unique=True, required=True)
    public = fields.StringField()
    secret = fields.StringField(required=True)

    meta = {'indexes': ['name']}

    @classmethod
    def get(cls, name):
        ret = cls.objects(name=name
                ).only('public', 'secret'
                ).first()
        return ret.public.encode('ascii'), ret.secret.encode('ascii')

    @classmethod
    def put(cls, name, public, secret):
        return cls(name=name, public=public, secret=secret).save()


get = SecretPair.get

put = SecretPair.put
