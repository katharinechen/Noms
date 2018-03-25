"""
Tests of the secret data
"""
import re

from pytest import raises

from noms import secret


def test_get(mockDatabase):
    """
    Can I get a manually-placed secret
    """
    sp = secret.SecretPair('hello', 'abc', '!@#')
    sp.save()
    assert secret.get('hello') == ('abc', '!@#')


def test_getDefault(mockDatabase):
    """
    Can I set a default if a secret is unfound?
    What if the item and the default are missing?
    """
    got = secret.get('NOTFOUND', ('a', 'b'))
    assert got == ('a', 'b')

    with raises(KeyError):
        secret.get('NOTFOUND')


def test_put(mockDatabase):
    """
    If I use the API to place a secret, can I get it from the db directly?
    """
    secret.put('grover', 'best', 'muppet')
    assert secret.SecretPair.objects.get(name='grover').secret == 'muppet'


def test_randomPassword():
    """
    Is it random enough?
    """
    sec1 = secret.randomPassword()
    sec2 = secret.randomPassword()
    assert re.match('[0-9abcdef]{64}', sec1)
    assert re.match('[0-9abcdef]{64}', sec2)
    assert sec1 != sec2
    sec3 = secret.randomPassword(10)
    assert re.match('[0-9abcdef]{20}', sec3)

