# vim:fileencoding=utf-8
"""
Test of package-level code contained in noms.__init__
"""
from pytest import raises

from noms import urlify


def test_urlify():
    """
    Do I produce punycode output for the inputs?
    """
    helloThere = u'你好'
    assert urlify(u'asdf', helloThere, u'69') == 'asdf--69-nm2mf94f'


def test_laziness(mockConfig):
    """
    Do I acquire a config object upon access?
    """
    del mockConfig.__dict__['_realConfig']
    mockConfig.apparentURL
    assert '_realConfig' in mockConfig.__dict__, "oops, test config should have _realConfig now but doesn't"


def test_attributeAccess(mockConfig):
    """
    Try out the attribute proxying properties
    """
    del mockConfig.__dict__['_realConfig']
    with raises(TypeError):
        setattr(mockConfig, 'uninitialized', 20)
    assert mockConfig.apparentURL == 'https://app.nomsbook.com'
    mockConfig.apparentURL = 'dfgkljdhf'
    assert mockConfig.apparentURL == 'dfgkljdhf'
