"""
Command-line interface for noms
"""

import mongoengine

from twisted.web import tap

from noms.server import Server
from noms import CONFIG

MAIN_FUNC = 'noms.cli.main'


class NomsOptions(tap.Options):
    optParameters = tap.Options.optParameters + [
            ['db', None, 'noms', 'Database name'],
            ['connect', None, None, 'Database connect string'],
            ]

    def postOptions(self):
        mongoengine.connect(self['db'], host=self['connect'])
        CONFIG.load()

        # now we know CONFIG exists
        cfg = CONFIG.require()
        cfg.cliOptions = dict(self.items())
        cfg.save()

        self.opt_class(MAIN_FUNC)

        return tap.Options.postOptions(self)


Options = NomsOptions


makeService = tap.makeService


def main():
    """
    Return a resource to start our application
    """
    print 'NOMS STARTUP', '=' * 40
    resource = Server().app.resource
    mongoengine.connect(CONFIG.cliOptions['db'], host=CONFIG.cliOptions['connect'])
    return resource()

