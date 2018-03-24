"""
Hooks for circusd to control startup
"""
import time
import shutil

from pymongo import errors

from mongoengine import connect


def before_start(watcher, arbiter, hook_name):
    time.sleep(0.5)
    return importSample()


def importSample():
    """
    Ensure sample data is available on this instance
    """
    try:
        from noms import DBHost, recipe
        from noms import whisk
        connect(**DBHost['noms'])
        if not recipe.Recipe.objects.count():
            print "First-time run. Installing fresh users and recipes."
            whisk.BaseWhisk.main(['sample'])
        print "%r connected" % DBHost['noms']['host']
        return True
    except errors.ServerSelectionTimeoutError:
        print "No mongo server available (tried %r)" % DBHost['noms']['host']
        return False
