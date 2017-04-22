"""
Set, get, and publish config for noms
"""
from boto import s3

from mongoengine import connect

from twisted.python.usage import UsageError

from codado.tx import Main, CLIError

from noms import (
        configuration, DBAlias,
        DBHost, secret,
        user
        )
from noms.whisk import describe


class Config(Main):
    """
    Command line to get/set/publish config values
    """
    synopsis = "config [[--push]|[--pull]|[--diff] OR var=newvalue]"

    optParameters = [
            ['alias', None, 'noms', 'Alias for a database connection (see noms.DBAlias)'],
            ]

    optFlags = [
            ['push', None, 'Upload current config to an s3 bucket'],
            ['pull', None, 'Download config from an s3 bucket'],
            ['diff', None, 'Show differences between current config and corresponding s3 bucket'],
            ]

    def parseArgs(self, var=None):
        self['set'] = var

    def postOptions(self):
        alias = self['alias']
        assert alias in DBAlias
        connect(**DBHost[alias])

        self.setdefault('set', None)

        # only one of these flags can be on
        if not True ^ self['push'] ^ self['pull'] ^ self['diff'] ^ bool(self['set']):
            raise UsageError("** Use only one of these: --push, --pull or --diff or var=value")

        if self['push']:
            return self.push()
        elif self['pull']:
            return self.pull()
        elif self['diff']:
            return self.diff()
        elif self['set']:
            return self.set()
        else:
            return self.show()

    @property
    def _config(self):
        cfg = configuration.Configuration.objects().first()
        if cfg is None:
            cfg = configuration.Configuration()
            cfg.save()
        return cfg

    def show(self):
        print self._config.to_json()

    def set(self):
        """
        Set a config value
        """
        k, v = self['set'].split('=', 1)
        setattr(self._config, k, v)
        self._config.save()

    def push(self):
        """
        Push our config to s3
        """
        1/0

    def pull(self):
        """
        Pull a closely-matching config from s3
        """
        1/0

    def diff(self):
        """
        Get the closest-matching config from s3 and compare to ours
        """
        1/0
