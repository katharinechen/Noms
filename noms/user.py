"""
Authentication and users
"""
from mongoengine import fields

from itsdangerous import (
        TimedJSONWebSignatureSerializer as Serializer
        )

from codado import enum

from noms.rendering import RenderableDocument


Roles = enum.fromkeys(['user', 'superuser'])


class User(RenderableDocument):
    """
    A person with a login account (or the ANONYMOUS user)
    """
    email = fields.StringField(require=True, unique=True)
    passwordHash = fields.StringField()
    roles = fields.ListField(fields.StringField(choices=Roles.keys()))
    givenName = fields.StringField()
    familyName = fields.StringField()

    meta = {'indexes': [
        'email',
        ]}

    def asToken(self):
        """
        Create a JSON token for this user
        """
        _, sec = secret.get('localapi')
        s = Serializer(sec, expires_in=secret.SECRET_EXPIRATION)
        return s.dumps({'email': self.email})

    @classmethod
    def fromSSO(cls, ssoData):
        """
        Create a local user from openid sso
        """
        d = enum(**ssoData)
        self = cls(
                email=d.email,
                givenName=d.given_name,
                familyName=d.family_name,
                roles=[Roles.user],
                )
        self.save()
        return self

    def safe(self):
        return dict(
                email=self.email,
                givenName=self.givenName,
                familyName=self.familyName,
                roles=self.roles
                )


_anonymous = User(
        email='anonymous@example.com', 
        roles=[Roles.user],
        givenName='Anonymous',
        )


def ANONYMOUS():
    """
    Ensure that the ANONYMOUS user exists in the database
    """
    global _anonymous
    if getattr(_anonymous, 'id', None):
        return _anonymous
    anon = User.objects(email=_anonymous.email).first()
    if anon is None:
        _anonymous.save(force_insert=True)
    assert _anonymous.id
    return _anonymous
