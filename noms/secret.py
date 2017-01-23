"""
Passwords, intended to be stored in the database
"""
import os

from mongoengine import fields

from noms import documentutil


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
    return ''.join('%x' % ord(c) for c in os.urandom(n))
