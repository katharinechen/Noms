"""
Tests for noms python code
"""
from functools import wraps

from mongoengine import connect

from twisted.internet import defer

from contextdecorator import contextmanager

from noms import DBAlias, DBHost
from noms import documentutil


# do this first so tests use the test db
_client = connect(**DBHost[DBAlias.nomsTest])


def wrapDatabaseAndCallbacks(fn):
    """
    Decorator; convenience for methods that need mock db and yield-Deferred syntax
    """
    fnICB = defer.inlineCallbacks(fn)
    fnMockedConfig = mockConfig()(fnICB)
    return wraps(fn)(fnMockedConfig)


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


@contextmanager
def mockDatabase():
    """
    Mongomock-based interface to a "database"
    """
    try:
        db = _client.get_default_database()
        _scrubMongoEngineBecauseMongoEngineIsSoStupid(_client, db)
        yield db
    finally:
        _scrubMongoEngineBecauseMongoEngineIsSoStupid(_client, db)


def _scrubMongoEngineBecauseMongoEngineIsSoStupid(client, db):
    """
    XXX - Mongoengine and mongomock do NOT work well together. Collection switching
    and other factors mean you have to scrub every collection, every time.
    Dropping the database doesn't work.
    """
    unsave()
    client.drop_database(db)


@contextmanager
def mockConfig(**configFields):
    """
    Define database connections for code that needs mongo
    """
    with mockDatabase() as db:
        try:
            cols = db.collection_names()
            docs = sum(db[c].count() for c in cols)
            assert docs == 0

            from noms.config import Config
            cfg = Config(**configFields)
            cfg.save()

            from noms import secret
            secret.put('auth0', 'abc123', 'ABC!@#')

            # in tests, we replace the global CONFIG without patching it
            from noms import CONFIG
            CONFIG.load()
            yield CONFIG

        finally:
            # despite dropping the database we have to do this, because it's
            # still an object in memory
            cfg.delete()

    del CONFIG.__dict__['_realConfig']


class ConfigMock(object):
    """
    Wraps a mock/unmock operation for config+database
    """
    def __init__(self, **configFields):
        self.cm = mockConfig(**configFields)
        self.config = self.cm.gen.next()

    def finish(self):
        try:
            self.cm.gen.next()
        except StopIteration:
            "Cleaning up"
