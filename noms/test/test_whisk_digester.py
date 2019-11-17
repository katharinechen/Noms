"""
Tests of the static digest command-line tool
"""
from twisted.internet import defer, task

import treq

from pytest import fixture
from pytest_twisted import inlineCallbacks

from mock import patch, Mock, ANY

from codado import fromdir

from noms.whisk import digester


TESTDIR_HASH = 'oregon-avocado-north'


@fixture
def testdir():
    return fromdir(__file__)('test_digester')


@fixture
def opt(testdir):
    o = digester.Digester()
    o.parseArgs(testdir)
    return o


def test_digest(testdir):
    """
    Do I produce a valid digest
    """
    dig = digester.digest(testdir)
    assert dig == TESTDIR_HASH


def test_postOptions(testdir, capsys, opt):
    """
    Do I generate a hash of the right dir?
    """
    opt.postOptions()
    out = capsys.readouterr()[0].strip()
    assert out == TESTDIR_HASH


@inlineCallbacks
def test_postOptionsWithUpdate(localapi, testdir, capsys, opt):
    """
    Do I connect to a noms instance and deliver the hash to it?
    """
    opt['update-url'] = 'https://nomsbook.com/sethash/'
    opt.parent = {'alias': 'nomsTest'}
    pReact = patch.object(task, 'react', lambda fn: fn(None))
    mContent = Mock(code=200)
    pGet = patch.object(treq, 'get',
                        return_value=defer.succeed(mContent),
                        autospec=True)
    with pReact, pGet as mGet:
        yield opt.postOptions()
        mGet.assert_called_once_with(
            'https://nomsbook.com/sethash/' + TESTDIR_HASH,
            headers={'x-token': ANY})
