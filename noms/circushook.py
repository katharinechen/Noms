"""
Hooks for circusd to control startup
"""
import time

from pymongo import errors

from mongoengine import connect


def before_start_importSample(watcher, arbiter, hook_name):
    """
    Ensure sample data is available on this instance
    """
    time.sleep(0.5)
    try:
        from noms import DBHost, recipe
        from noms.whisk import sample
        connect(**DBHost['noms'])
        if not recipe.Recipe.objects.count():
            print "First-time run. Installing fresh users and recipes."
            sample.Sample.postOptions()
        print "%r connected" % DBHost['noms']['host']
        return True
    except errors.ServerSelectionTimeoutError:
        print "No mongo server available (tried %r)" % DBHost['noms']['host']
        return False
