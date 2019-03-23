# vim:fileencoding=utf-8
"""
Test of package-level code contained in noms.__init__
"""
from pytest_twisted import inlineCallbacks

from twisted.internet import defer

from noms import urlify
from noms.test import conftest


def test_urlify():
    """
    Do I produce punycode output for the inputs?
    """
    helloThere = u'你好'
    assert urlify(u'asdf', helloThere, u'69') == 'xn--asdf--69-nm2mf94f'
    whatsUp = u"what's up"
    assert urlify(u'asdf', whatsUp, u'69') == 'asdf-what-s-up-69'


def test_laziness(mockConfig):
    """
    Do I acquire a Configuration object upon access?
    """
    mockConfig.public_hostname
    assert 'description' in mockConfig.__dict__, "oops, test config should have description now but doesn't"


def test_attributeAccess(mockConfig):
    """
    Try out the attribute proxying properties
    """
    assert mockConfig.public_hostname == 'app.nomsbook.com'
    mockConfig.public_hostname = 'dfgkljdhf'
    assert mockConfig.public_hostname == 'dfgkljdhf'


@inlineCallbacks
def test_assertFailure():
    """
    Does assertFailure catch failures, and also fail when failures don't fail?
    """
    d = defer.execute(lambda: 1/0)
    yield conftest.assertFailure(d, ZeroDivisionError)

    # assertFailure with wrong exception type is a failed assertFailure
    d = defer.execute(lambda: 1/0)
    dd = conftest.assertFailure(d, TypeError)
    yield conftest.assertFailure(dd, AssertionError)

    # assertFailure without a failure is a failed assertFailure
    d = conftest.assertFailure(defer.succeed(None), TypeError)
    yield conftest.assertFailure(d, AssertionError)
