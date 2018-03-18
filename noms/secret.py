"""
Passwords, intended to be stored in the database
"""
import os
import base64

from mongoengine import fields

from twisted.internet import defer
import txk8s

from noms import documentutil


NO_DEFAULT = object()
SECRET_EXPIRATION = 600 # 10 minutes

K8S_NS = 'dev-nomsbook-com'
K8S_SECRET_LABEL = 'nomsbook.com/v1-secretpair'


class SecretPair(documentutil.NomsDocument):
    """
    A named password, auth token, or other secret with its public pair
    """
    name = fields.StringField(unique=True, required=True)
    public = fields.StringField()
    secret = fields.StringField(required=True)

    meta = {'indexes': ['name']}

    @classmethod
    def get(cls, name, default=NO_DEFAULT):
        ret = cls.objects(name=name
                ).only('public', 'secret'
                ).first()

        if ret is None:
            if default is NO_DEFAULT:
                raise KeyError(name)
            return default

        return ret.public.encode('ascii'), ret.secret.encode('ascii')

    @classmethod
    def put(cls, name, public, secret):
        return cls(name=name, public=public, secret=secret).save()

    @defer.inlineCallbacks
    def putK8s(self):
        """
        Store the secret in kubernetes, using the following data structure:

        ```
        metadata:
            name: (self.name)
            labels:
                - (K8s_SECRET_LABEL):
        data:
            public: (self.public)
            secret: (self.secret)
        ```
        """
        txcli = txk8s.TxKubernetesClient()

        # let's create and store a secret
        pub_b64 = base64.b64encode(self.public)
        sec_b64 = base64.b64encode(self.secret)
        meta = txcli.V1ObjectMeta(name=self.name, labels={K8S_SECRET_LABEL: ''})
        body = txcli.V1Secret(data={'public': pub_b64, 'secret': sec_b64}, metadata=meta)

        res = yield txcli.call(txcli.coreV1.create_namespaced_secret, K8S_NS, body)
        print('Create and store: %r: %r\n' % (res.metadata.self_link, res.data))
        defer.returnValue(res)


get = SecretPair.get

put = SecretPair.put


def randomPassword(n=32):
    """
    Produce a string n*2 bytes long, of hex digits
    """
    return ''.join('%02x' % ord(c) for c in os.urandom(n))


@defer.inlineCallbacks
def loadFromK8s():
    """
    Fetch secrets from kubernetes

    Does nothing if the secret_pair collection already exists; to force, drop
    the secret_pair collection.
    """
    from noms import user

    txcli = txk8s.TxKubernetesClient()

    lst = yield txcli.call(txcli.coreV1.list_namespaced_secret, K8S_NS, label_selector=K8S_SECRET_LABEL)
    if not lst.items:
        print("ERROR: no secrets in", K8S_NS, "having label =", K8S_SECRET_LABEL)
        return

    added = []
    for item in lst.items:
        if item.metadata.name in user.USERS:
            continue
        # recreate all available secrets from cluster every boot
        SecretPair.objects(name=item.metadata.name).delete()
        secpair = SecretPair(
            name=item.metadata.name, 
            public=item.data['public'], 
            secret=item.data['secret'])
        secpair.save()
        added.append(secpair)
    print("Piping hot fresh secrets from %r: %r" % (K8S_NS, [n.name for n in added]))

