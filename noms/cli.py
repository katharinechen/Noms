"""
Command-line interface for noms
"""
import subprocess 

from twisted.web import tap

from mongoengine import connect

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
        alias = self['alias']
        assert alias in DBAlias
        connect(**DBHost[alias])
        CONFIG.load()
        
        # now we know CONFIG exists
        CONFIG.cliOptions = dict(self.items())
        CONFIG.save()

        # run Sass
        bashCommand = "sass --watch static/scss/base.scss:static/css/base.css --trace"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

        self.opt_class(MAIN_FUNC)

        return tap.Options.postOptions(self)


Options = NomsOptions


makeService = tap.makeService


def main():
    """
    Return a resource to start our application
    """
    resource = Server().app.resource
    alias = CONFIG.cliOptions['alias']
    connect(**DBHost[alias])
    return resource()

