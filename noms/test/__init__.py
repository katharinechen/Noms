"""
Tests for noms python code
"""
from contextlib import contextmanager

from mongoengine import connect


REPLACE_DB = "noms-test"
REPLACE_DB_HOST = "mongomock://localhost"


@contextmanager
def mockDatabase(replaceDB=REPLACE_DB,
        host=REPLACE_DB_HOST):
    """
    Mongomock-based interface to a "database"
    """
    con = connect(None, host=host, alias='default')
    con.drop_database(replaceDB)
    yield getattr(con, replaceDB)
    con.drop_database(replaceDB)


@contextmanager
def mockConfig(replaceDB=REPLACE_DB,
        host=REPLACE_DB_HOST,
        **configFields):
    """
    Define database connections for code that needs mongo
    """
    with mockDatabase(replaceDB, host):
        from noms import config
        cfg = config.Config(**configFields)
        cfg.save()
        yield cfg


class ConfigMock(object):
    """
    Wraps a mock/unmock operation for config+database
    """
    def __init__(self,
            replaceDB=REPLACE_DB,
            host=REPLACE_DB_HOST,
            **configFields):
        self.cm = mockConfig(replaceDB, host, **configFields)
        self.config = self.cm.gen.next()

    def finish(self):
        try:
            self.cm.gen.next()
        except StopIteration:
            "Cleaning up"
