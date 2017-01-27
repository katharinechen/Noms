"""
Tests of the urltool command-line program
"""
import re

from werkzeug.routing import Rule

from pytest import fixture

from noms.server import APIServer, Server
from noms import urltool

def test_dumpRule():
    """
    Do I produce the correct data structure for a rule?
    """
    rule = Rule('/sethash/', endpoint='setHash')
    x = urltool.dumpRule(APIServer, rule, '/grover')
    assert x == {'/grover/sethash/': {
        'endpoint': 'APIServer.setHash',
        'roles': ['localapi'],
        }}

    rule2 = Rule('/api/', endpoint='api_branch')
    x2 = urltool.dumpRule(Server, rule2, '')
    assert x2 == {'/api/': {
        'branch': True,
        'endpoint': 'Server.api',
        }}


@fixture
def options():
    return urltool.Options()


def test_parseArgs(options):
    """
    Do I correct default the filter argument
    """
    options.parseArgs()
    assert options['filt'] == re.compile('.*')
    options.parseArgs('hello')
    assert options['filt'] == re.compile('hello')
