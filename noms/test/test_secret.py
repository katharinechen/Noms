"""
Tests of the secret data
"""
import re

from pytest import raises, mark, fixture

from mock import patch, MagicMock

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


@fixture
def s3client():
    """
    An s3 resource with appropriate mocks
    """
    devBucket = MagicMock(name='Bucket Dev')
    devBucket.name = 'config.dev.nomsbook.com'
    devJSON = '{"_id":{"$oid":"65dd13ca8a99d245c1f7fdd4"},"name":"auth0","public":"devnomsbookcom_auth0_key","secret":"debnomsbookcom_auth0_secret"}'
    devBucket.download_fileobj = MagicMock(name='download_fileobj',
            side_effect=lambda s, io: io.write(devJSON))

    coryBucket = MagicMock(name='Bucket Cory')
    coryBucket.name = 'config.cory.ngrok.io'
    coryJSON = '{"_id":{"$oid":"65dd13ca8a99d245c1f7fdd4"},"name":"auth0","public":"coryngrokio_auth0_key","secret":"coryngrokio_auth0_secret"}'
    coryBucket.download_fileobj = MagicMock(name='download_fileobj', 
            side_effect=lambda s, io: io.write(coryJSON))

    ret = MagicMock(name='S3 Resource')
    ret.Bucket = MagicMock()
    ret.Bucket.return_value = devBucket
    ret.buckets.all.return_value = [devBucket, coryBucket]

    with patch.object(secret.boto3, 'resource', return_value=ret):
        yield ret


@mark.parametrize('public_hostname,expected', [
        ['app.nomsbook.com', 'devnomsbookcom_auth0_key'],
        ['dev.nomsbook.com', 'devnomsbookcom_auth0_key'],
        ['cory.ngrok.io', 'coryngrokio_auth0_key'],
        ])
def test_loadFromS3(public_hostname, expected, mockConfig, s3client):
    """
    Do I get secrets from the right bucket, given a set of buckets and a
    certain hostname?
    """
    with patch.object(secret, 'CONFIG', mockConfig):
        # purge the secrets our test fixture normally adds
        secret.SecretPair.objects.delete()

        mockConfig.public_hostname = public_hostname
        secret.loadFromS3()
        assert secret.get('auth0')[0] == expected
