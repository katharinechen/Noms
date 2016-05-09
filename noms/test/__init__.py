"""
Tests for noms python code
"""

from mongoengine import connect
from mongoengine.connection import disconnect


REPLACE_DB = "noms-test"


def resetDatabase(replaceDB=REPLACE_DB):
    """
    Define database connections for code that needs mongo
    """
    disconnect()
    # register_connection(replaceDB, replaceDB)
    con = connect(replaceDB)
    nomsTestDB = getattr(con, replaceDB)
    for name in nomsTestDB.collection_names(include_system_collections=False):
        coll = getattr(nomsTestDB, name)
        coll.remove()

