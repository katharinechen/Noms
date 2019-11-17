"""
Fixtures and common options for pytest tests
"""
from cStringIO import StringIO
import json

from pytest import fixture

from mock import patch

from mongoengine import connect, Document
from mongoengine.connection import disconnect

from codado import fromdir

from crosscap.testing import DEFAULT_HEADERS, request

from noms import DBAlias, DBHost, documentutil, user
from noms.whisk import describe


_client = None


@fixture(scope='session', autouse=True)
def useTheTestDatabase():
    """
    When starting to test, connect to the test database, making it the default
    connection, and pre-empting other code that connects to the database.
    """
    global _client
    with patch.dict(DBHost, {'noms': DBHost[DBAlias.nomsTest]}):
        if _client is None:
            _client = connect(**DBHost[DBAlias.nomsTest])
        yield
        disconnect()


class _MongoEngineHack(Document):
    """
    Document class solely for the purpose of getting access to the db object.

    This is the easiest way to find the db, since get_default_database is
    broken.
    """


@fixture
def mockDatabase():
    """
    Mongomock-based interface to a "database"
    """
    try:
        db = _MongoEngineHack._get_db()
        _scrubMongoEngineBecauseMongoEngineIsSoStupid(_client, db)
        yield db
    finally:
        _scrubMongoEngineBecauseMongoEngineIsSoStupid(_client, db)


def assertFailure(deferred, *expectedFailures):
    """
    Fail if C{deferred} does not errback with one of C{expectedFailures}.
    Returns the original Deferred with callbacks added. You will need
    to return this Deferred from your test case.

    *COPIED SHAMELESSLY FROM twisted.trial._asynctest.TestCase*
    """
    def _cb(ignore):
        raise AssertionError(
            "did not catch an error, instead got %r" % (ignore,))

    def _eb(failure):
        if failure.check(*expectedFailures):
            return failure.value
        else:
            output = ('\nExpected: %r\nGot:\n%s'
                      % (expectedFailures, str(failure)))
            raise AssertionError(output)
    return deferred.addCallbacks(_cb, _eb)


def onSave(doc):
    """
    Hook into Document.save() and keep a reference to any object in our
    application that was saved. We can later call unsave() to remove them.
    """
    _unsaves.add(doc)


_unsaves = set()

documentutil.onSave = onSave


def unsave():
    """
    Remove all Document instances which were previously saved by tests
    """
    for x in _unsaves:
        x.delete()

    _unsaves.clear()


def _scrubMongoEngineBecauseMongoEngineIsSoStupid(client, db):
    """
    XXX - Mongoengine and mongomock do NOT work well together. Collection switching
    and other factors mean you have to scrub every collection, every time.
    Dropping the database doesn't work.
    """
    unsave()
    client.drop_database(db)


@fixture
def mockConfig(mockDatabase):
    """
    Wrap a fake config object into each test request along with a mock database
    """
    # in tests, we replace the global CONFIG without patching it
    import noms

    try:
        cols = mockDatabase.collection_names()
        for c in cols:  # pragma: nocover
            assert mockDatabase[c].count() == 0, c + " not empty"

        cfg = noms.Config()
        descr = describe.Description()
        descr.public_hostname = ('cli', 'app.nomsbook.com')
        cfg.description = descr
        cfg.staticHash = 'asdfasdfsdaf'

        from noms import secret
        secret.put('auth0', 'abc123', 'ABC!@#')
        secret.put('localapi', 'localapi', '!@#ABC')

        with patch.object(noms, 'CONFIG', cfg):
            yield cfg

    finally:
        # despite dropping the database we have to do this, because it's
        # still an object in memory
        for c in cols:  # pragma: nocover
            col = mockDatabase[c]
            col.remove()
            assert col.count() == 0, "%r not empty" % c


@fixture
def specialUsers():
    """
    Preload the special users
    """
    from noms import user
    user.USER()


@fixture
def weirdo(mockConfig):
    """
    Preload the weirdo user

    The mockConfig fixture here is required so that the User object has a
    collection pointing to the mock database, otherwise it wouldn't be
    possible to save it in the mock database.
    """
    from noms import user
    return user.User(
        email='weirdo@gmail.com',
        givenName='Weirdo',
        familyName='User',
        roles=[user.Roles.user]).save()


@fixture
def localapi(mockConfig):
    """
    Save a copy of localapi in the mock db
    """
    localapi = user.User(
        email='localapi@example.com',
        roles=[user.Roles.localapi],
        givenName='Local API',
    )
    localapi.save()
    return localapi


@fixture
def recipePageHTML():
    return open(fromdir(__file__)('recipe_page_source.html')).read()


@fixture
def recipeData():
    """
    Provide recipe that can be used successfully in tests
    """
    recipeData = {
        "author": u"Cory Dodt",
        "name": u"Delicious Meatless Meatballs",
        "email": u"weirdo-gmail-com",
        "ingredients": ["one", "two"],
        "instructions": ["instruction-one", "instruction-two"]
    }
    return recipeData


def requestJSON(postpath, requestHeaders=DEFAULT_HEADERS, responseHeaders=(), **kwargs):
    """
    As ServerTest.request, but force content-type header and look for other
    convenience args:

    - coerce kwargs['content'] to set the post body (can be a str or dict)
    - if kwargs['user'] is a user object, use it to set the auth token
    """
    content = kwargs.pop('content', None)
    if isinstance(content, dict):
        kwargs['content'] = StringIO(json.dumps(content))
    elif content:  # pragma: nocover
        kwargs['content'] = StringIO(str(content))
    else:
        kwargs['content'] = None

    # create a user token from the user arg if seen
    user = kwargs.pop('user', None)
    if user:
        tok = user.asToken()
        requestHeaders = requestHeaders + (('x-token', [tok]),)

    responseHeaders = responseHeaders + (('content-type', 'application/json'),)
    req = request(postpath, requestHeaders, responseHeaders, **kwargs)

    return req
