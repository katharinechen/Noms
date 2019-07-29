"""
Hooks for circusd to control startup
"""
import os
import time

from pymongo import errors

from mongoengine import connect


def before_start(watcher, arbiter, hook_name):
    time.sleep(0.5)
    return importSample() and cleanDevEnvironment()


def cleanDevEnvironment():
    """
    Fix problems doing development inside a container:

    When doing development inside a container, where we are editing our local source files
    (e.g. a Mac host running the noms service inside a Linux docker container with),
    there are certain issues that have to be cleaned up/rebuilt before running Noms.
    """
    os.system("npm rebuild node-sass")
    return True


def importSample():
    """
    Ensure sample data is available on this instance
    """
    try:
        from noms import DB_CONNECT, DB_NAME, recipe
        from noms import whisk
        connect(DB_NAME, DB_CONNECT)
        if not recipe.Recipe.objects.count():
            print("First-time run. Installing fresh users and recipes.")
            whisk.BaseWhisk.main(['sample'])
        print("%r connected" % DB_CONNECT)
        return True
    except errors.ServerSelectionTimeoutError:
        print("No mongo server available (tried %r)" % DB_CONNECT)
        return False
