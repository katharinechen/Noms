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


cwr = reactor.callWhenRunning


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

        # schedule these to run:

        # - get secrets from aws and store them in mongo
        cwr(secret.loadFromS3)
        # - initialize 'user' and 'localapi' users
        cwr(userLoadLocalapi)
        cwr(userLoadDefaultUser)

        # - start watchmedo to look for staticHash changes
        cwr(subprocessRunWatchmedo)
        # - start node-sass to watch for scss changes and rebuild css
        cwr(subprocessRunNodeSass)

        self.opt_class(MAIN_FUNC)

        tap.Options.postOptions(self)


Options = Run

makeService = tap.makeService


def userLoadLocalapi():
    """
    At reactor startup, install the localapi user with a random password
    """
    # store an internally-shared secret
    if not secret.get('localapi', None):
        password = secret.randomPassword()
        secret.put('localapi', 'localapi', password)
        print("Stored new localapi password")


def userLoadDefaultUser():
    """
    At reactor startup, install the default 'user' user
    """
    user.USER()


def subprocessRunWatchmedo():
    """
    At reactor startup, run watchmedo, the process that updates the cache busting hash
    """
    # compute the current static digest hash
    staticPath = '%s/static' % os.getcwd()
    CONFIG.staticHash = digest(staticPath)

    # watch for changes to static files (cache busting)
    watchCL = "watchmedo shell-command --patterns='{pat}' --recursive --command='{cmd}' {where}"
    watchCL = watchCL.format(
        pat=STATIC_FILE_PATTERNS,
        cmd='whisk digester -U %s/api/sethash/ %s' % (FIXME_LOCALAPI_URL, staticPath),
        where=staticPath,
        )
    subprocess.Popen(shlex.split(watchCL), stdout=subprocess.PIPE)


def subprocessRunNodeSass():
    """
    At reactor startup, run node-sass and watch scss for changes to keep the CSS files uptodate
    """
    # run Sass
    sassCL = "node-sass -w static/scss/base.scss -o static/css"

    subprocess.Popen(shlex.split(sassCL), stdout=subprocess.PIPE)


def main():
    """
    Return a resource to start our application
    """
    return Server().app.resource()

