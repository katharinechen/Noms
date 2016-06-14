"""
Command-line interface for noms
"""

from mongoengine import register_connection

from twisted.web import tap

from noms.server import Server
from noms import CONFIG, DBAlias, DBHost


MAIN_FUNC = 'noms.cli.main'


class NomsOptions(tap.Options):
    """
    A tap options object suitable for twistd to start, with noms-specific extras
    """
    optParameters = tap.Options.optParameters + [
            ['alias', None, 'noms', 'Alias for a database connection (see noms.DBAlias)'],
            ]

    def postOptions(self):
        """
        Connect to the noms database and make sure a config exists
        """
        assert self['alias'] in DBAlias.keys()
        register_connection('default', host=DBHost[self['alias']])
        CONFIG.load()

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
    register_connection('default', host=DBHost[CONFIG.cliOptions['alias']])
    return resource()

