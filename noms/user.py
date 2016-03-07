"""
Authentication and users
"""

from mongoengine import Document, fields

from noms import enum


Roles = enum.fromkeys(['user', 'superuser'])


class User(Document):
    email = fields.StringField(require=True, unique=True)
    passwordHash = fields.StringField()
    roles = fields.ListField(fields.StringField(choices=Roles.keys()))
    givenName = fields.StringField()
    familyName = fields.StringField()

    meta = {'indexes': [
        'email',
        ]}

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

    def toJSType(self):
        return dict(
                email=self.email,
                givenName=self.givenName,
                familyName=self.familyName,
                roles=self.roles
                )
