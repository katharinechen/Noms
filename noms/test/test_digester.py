"""
Tests of the static digest command-line tool
"""
from pytest import fixture

from codado import fromdir

from noms import digester


@fixture
def testdir():
    return fromdir(__file__)('test_digester')


def test_digest(testdir):
    """
    Do I produce a valid digest
    """
    dig = digester.digest(testdir)
    assert dig == 'oregon-avocado-north'
