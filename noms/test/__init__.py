"""
Tests for noms python code
"""
from contextlib import contextmanager

from mongoengine import connect

from noms import DBAlias, DBHost


# do this first so tests use the test db
_client = connect(**DBHost[DBAlias.nomsTest])


@contextmanager
def mockDatabase():
    """
    Mongomock-based interface to a "database"
    """
    try:
        db = _client.get_default_database()
        _client.drop_database(db)
        yield db
    finally:
        _client.drop_database(db)


@contextmanager
def mockConfig(**configFields):
    """
    Define database connections for code that needs mongo
    """
    with mockDatabase() as db:
        try:
            cols = db.collection_names()
            docs = 0
            for c in cols:
                docs += db[c].count()
            assert docs == 0
            from noms.config import Config
            ct = Config.objects.count()
            cfg = Config(**configFields)
            cfg.save()

            # in tests, we replace the global CONFIG without patching it
            from noms import CONFIG
            CONFIG.load()
            yield CONFIG

        finally:
            cfg.delete()
    del CONFIG.__dict__['_realConfig']

    ct = Config.objects.count()
    if not ct == 0:
        import pdb; pdb.set_trace()


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
