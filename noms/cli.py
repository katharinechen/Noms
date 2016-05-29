"""
Command-line interface for noms
"""

import mongoengine

from twisted.web import tap

from noms.server import Server
from noms import config, CONFIG

MAIN_FUNC = 'noms.cli.main'


class NomsOptions(tap.Options):
    """
    A tap options object suitable for twistd to start, with noms-specific extras
    """
    optParameters = tap.Options.optParameters + [
            ['db', None, 'noms', 'Database name or connect string'],
            ]

    def postOptions(self):
        """
        Connect to the noms database and make sure a config exists
        """
        mongoengine.connect(db=self['db'])
        # check to see if there is any config
        if not CONFIG.require():
            config.Config().save()

        # now we know CONFIG exists
        CONFIG.cliOptions = dict(self.items())
        CONFIG.save()

        self.opt_class(MAIN_FUNC)

        return tap.Options.postOptions(self)


Options = NomsOptions


makeService = tap.makeService


def main():
    """
    Return a resource to start our application
    """
    resource = Server().app.resource
    mongoengine.connect(db=CONFIG.cliOptions['db'])
    return resource()

