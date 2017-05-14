"""
Command-line interface for noms
"""
import os
import shlex
import subprocess
import time

from twisted.web import tap
from twisted.internet import reactor

from mongoengine import connect

from tqdm import trange

from noms.server import Server
from noms import CONFIG, DBAlias, DBHost, user, secret
from noms.whisk.digester import digest


MAIN_FUNC = 'noms.cli.main'
FIXME_LOCALAPI_URL = 'http://localhost:8080'
STATIC_FILE_PATTERNS = '*.js;*.css;*.html;*.json;*.gif;*.png;*.eot;*.woff;*.otf;*.svg;*.ttf'


class Run(tap.Options):
    """
    Start the noms thing
    """
    optParameters = tap.Options.optParameters + [
            ['alias', None, 'noms', 'Alias for a database connection (see noms.DBAlias)'],
            ]

    def postOptions(self):
        """
        Connect to the noms database and make sure a config exists
        """
        # If noms crashes, we'll wait 5 minutes to aid troubleshooting.
        trig = reactor.addSystemEventTrigger('after', 'shutdown', shutdownWait, 300)
        # If noms doesn't crash within the first 5 minutes, never mind; at
        # that point we probably want to shut down as fast as possible.
        reactor.callLater(300, reactor.removeSystemEventTrigger, trig)

        alias = self['alias']
        assert alias in DBAlias
        connect(**DBHost[alias])
        
        # compute the current static digest hash
        staticPath = '%s/static' % os.getcwd()
        CONFIG.staticHash = digest(staticPath)

        # get secrets from aws and store them in mongo
        secret.loadFromS3()

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
            cmd='digester -U %s/api/sethash/ %s' % (FIXME_LOCALAPI_URL, staticPath),
            where=staticPath,
            )
        subprocess.Popen(shlex.split(watchCL), stdout=subprocess.PIPE)

        # run Sass
        sassCL = "bundle exec sass --watch static/scss/base.scss:static/css/base.css --trace"
        subprocess.Popen(shlex.split(sassCL), stdout=subprocess.PIPE)

        self.opt_class(MAIN_FUNC)

        tap.Options.postOptions(self)


def shutdownWait(n):
    """
    Wait a certain number of seconds (with progress bar).

    Used to delay a restart when noms has crashed.
    """
    print "Noms crashed. Waiting..."
    for n in trange(n):
        time.sleep(1)


Options = Run

makeService = tap.makeService


def main():
    """
    Return a resource to start our application
    """
    return Server().app.resource()

