"""
Authentication and users
"""
from mongoengine import fields

from twisted.python.components import registerAdapter
from twisted.web.server import Request

from itsdangerous import (
        URLSafeTimedSerializer as Serializer,
        BadSignature,
        SignatureExpired)


from codado import enum

from noms.rendering import RenderableDocument
from noms.interface import ICurrentUser
from noms import secret


Roles = enum.fromkeys([
    'anonymous',
    'user',
    'superuser',
    'localapi',
    ])


class User(RenderableDocument):
    """
    A person with a login account (or the Anonymous user)
    """
    email = fields.StringField(require=True, unique=True)
    passwordHash = fields.StringField()
    roles = fields.ListField(fields.StringField(choices=list(Roles.keys())))
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

    def safe(self):
        return dict(
                email=self.email,
                givenName=self.givenName,
                familyName=self.familyName,
                roles=self.roles
                )

    @classmethod
    def fromRequest(cls, request):
        """
        Return the user this request session belongs to.

        This may be done by inspecting the token if it is available or by
        inspecting the session (using the cookie as the key).
        """
        # 1. Inspect the authorization header to see whether we're getting a token
        u = cls._fromAuthToken(request)
        if u:
            return u

        # 2. Look for a browser session by the session cookie
        u = cls._fromSession(request)
        if u:
            return u

        return USER().anonymous

    @classmethod
    def _fromAuthToken(cls, request):
        """
        Check a JSON token to see if it's validly signed
        """
        token = request.getHeader('x-token')
        if not token:
            return None

        _, sec = secret.get('localapi')
        s = Serializer(sec)
        try:
            data = s.loads(token, max_age=secret.SECRET_EXPIRATION)
        except (BadSignature, SignatureExpired):
            return None

        u = User.objects(email=data['email']).first()
        assert u, "Got a VALID token for %r, who does not exist??" % data['email']
        return u

    @classmethod
    def _fromSession(cls, request):
        """
        Check the user session for a user
        """
        return getattr(request.getSession(), 'user', None)

    def asToken(self):
        """
        Create a JSON token for this user
        """
        _, sec = secret.get(u'localapi')
        s = Serializer(sec)
        return s.dumps({'email': self.email})


registerAdapter(User.fromRequest, Request, ICurrentUser)


_USERS = enum(
    anonymous=User(
        email='anonymous@example.com',
        roles=[Roles.anonymous],
        givenName='Anonymous',
        ),
    localapi=User(
        email='localapi@example.com',
        roles=[Roles.localapi],
        givenName='Local API',
        ),
    )


def USER():
    """
    Ensure that the special users exist in the database

    => enum of those users
    """
    for k, _U in _USERS.items():
        if getattr(_U, 'id', None):
            "Already created and saved these users"
            continue
        u = User.objects(email=_U.email).first()
        if u is None:
            "Never saved before"
            _U.save()
        else: # pragma: nocover
            "Swapping in-mem user object with one we found on disk"
            _USERS[k] = _U = u
        assert _U.id

    return _USERS
