"""
Set, get, and publish config for noms
"""
from boto import s3

from codado.tx import Main, CLIError

from noms import (
        CONFIG, config, DBAlias,
        DBHost, describe, secret,
        user
        )


class Config(Main):
    """
    Command line to get/set/publish config values
    """
    optParameters = [
            ['alias', None, 'noms', 'Alias for a database connection (see noms.DBAlias)'],
            ]

    optFlags = [
            ['push', None, 'Upload current config to an s3 bucket'],
            ['pull', None, 'Download config from an s3 bucket'],
            ['compare', None, 'Show differences between current config and corresponding s3 bucket'],
            ]

    def postOptions(self):
        alias = self['alias']
        assert alias in DBAlias
        connect(**DBHost[alias])
        CONFIG.load()

        description = describe.Description.build()

