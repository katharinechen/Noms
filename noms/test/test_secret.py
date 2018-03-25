"""
Tests of the secret data
"""
import re

from twisted.internet import defer

import txk8s

from pytest import raises, fixture, inlineCallbacks

from mock import patch, MagicMock as MM

from noms import secret


@fixture
def txk8sClientLoad():
    """
    A substitute client for txkubernetes
    """
    one = MM(data={'public': '1', 'secret': '1s'})
    one.metadata.name = 'one'
    two = MM(data={'public': '2', 'secret': '2s'})
    two.metadata.name = 'two'
    three = MM(data={'public': '3', 'secret': '3s'})
    three.metadata.name = 'localapi'
    cli = MM()
    d = defer.succeed(MM(items=[one, two, three]))
    cli.call.return_value = d
    return cli


@fixture
def txk8sClientLoadEmpty():
    """
    A substitute client for txkubernetes, returning no secrets
    """
    cli = MM()
    d = defer.succeed(MM(items=[]))
    cli.call.return_value = d
    return cli


@fixture
def txk8sPutClient():
    """
    A substitute client for txkubernetes, configured for creating a secret
    """
    cli = MM()
    ret = MM()
    ret.metadata.self_link = 'foo.com/bar'
    ret.data = 'serkit'
    d = defer.succeed(ret)
    cli.call.return_value = d
    return cli


@inlineCallbacks
def test_loadFromK8s(mockDatabase, txk8sClientLoad, txk8sClientLoadEmpty):
    """
    Do we interpret the API response from k8s as data correctly?
    """
    pClient = patch.object(txk8s, 'TxKubernetesClient', return_value=txk8sClientLoad)
    # try normally
    with pClient:
        res = yield secret.loadFromK8s()
        assert len(res) == 2
        assert (res[0].public, res[1].public) == ('1', '2')

    # test with empty response
    pClient = patch.object(txk8s, 'TxKubernetesClient', return_value=txk8sClientLoadEmpty)
    with pClient:
        res = yield secret.loadFromK8s()
        assert res is None


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


@inlineCallbacks
def test_putK8s(mockDatabase, txk8sPutClient):
    """
    Do I invoke the k8s API to store this secret?
    """
    pClient = patch.object(txk8s, 'TxKubernetesClient', return_value=txk8sPutClient)
    with pClient as mClient:
        fn = mClient.return_value.coreV1.create_namespaced_secret
        k8sSecretObj = mClient.return_value.V1Secret.return_value
        sp = secret.SecretPair(name='one', public='1', secret='1s')
        res = yield sp.putK8s()
        mClient.return_value.call.assert_called_once_with(
            fn,
            'dev-nomsbook-com',
            k8sSecretObj
            )
        assert res.data == 'serkit'


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

