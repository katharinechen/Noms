"""
Command-line interface for noms
"""
import subprocess
import os
import shlex

from twisted.web import tap

from mongoengine import connect

from noms.server import Server
from noms import CONFIG, DBAlias, DBHost, user, secret
from noms.digester import digest


MAIN_FUNC = 'noms.cli.main'
FIXME_URL = 'http://localhost:8080'
STATIC_FILE_PATTERNS = '*.js;*.css;*.html;*.json;*.gif;*.png;*.eot;*.woff;*.otf;*.svg;*.ttf'


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
        staticPath = '%s/static' % os.getcwd()
        CONFIG.staticHash = digest(staticPath)
        CONFIG.save()

        # store an internally-shared secret
        if not secret.get('localapi', None):
            password = secret.randomPassword()
            secret.put('localapi', 'localapi', password)
            print "Stored new localapi password"

        # ensure that at least the special users exist
        user.USER()

        # watch for changes to static files (cache busting)
        watchCommand = "watchmedo shell-command --patterns='{pat}' --recursive --command='{cmd}' {where}"
        watchCommand = watchCommand.format(
            pat=STATIC_FILE_PATTERNS,
            cmd='digester -U %s/api/sethash/ %s' % (FIXME_URL, staticPath),
            where=staticPath,
            )
        subprocess.Popen(shlex.split(watchCommand), stdout=subprocess.PIPE)

        # run Sass
        bashCommand = "sass --watch static/scss/base.scss:static/css/base.css --trace"
        subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

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

