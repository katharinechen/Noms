"""
Command-line interface for noms
"""
import os
import shlex
import subprocess

from twisted.internet import reactor
from twisted.web import tap

from mongoengine import connect

from noms.server import Server
from noms import CONFIG, DBAlias, DBHost, user, secret
from noms.whisk.digester import digest


MAIN_FUNC = 'noms.cli.main'
FIXME_LOCALAPI_URL = 'http://localhost:8080'
STATIC_FILE_PATTERNS = '*.js;*.css;*.html;*.json;*.gif;*.png;*.eot;*.woff;*.otf;*.svg;*.ttf'


class Run(tap.Options):
    """
    Run noms
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

        # compute the current static digest hash
        staticPath = '%s/static' % os.getcwd()
        CONFIG.staticHash = digest(staticPath)

        # get secrets from aws and store them in mongo
        reactor.callWhenRunning(secret.loadFromS3)

        # store an internally-shared secret
        if not secret.get('localapi', None):
            password = secret.randomPassword()
            secret.put('localapi', 'localapi', password)
            print "Stored new localapi password"

        # ensure that at least the special users exist
        user.USER()

        # watch for changes to static files (cache busting)
        watchCL = "watchmedo shell-command --patterns='{pat}' --recursive --command='{cmd}' {where}"
        watchCL = watchCL.format(
            pat=STATIC_FILE_PATTERNS,
            cmd='whisk digester -U %s/api/sethash/ %s' % (FIXME_LOCALAPI_URL, staticPath),
            where=staticPath,
            )
        subprocess.Popen(shlex.split(watchCL), stdout=subprocess.PIPE)

        # run Sass
        sassCL = "node-sass -w static/scss/base.scss -o static/css"

        subprocess.Popen(shlex.split(sassCL), stdout=subprocess.PIPE)

        self.opt_class(MAIN_FUNC)

        tap.Options.postOptions(self)


Options = Run

makeService = tap.makeService


def main():
    """
    Return a resource to start our application
    """
    return Server().app.resource()

