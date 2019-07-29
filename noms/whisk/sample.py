#!/usr/bin/env python
"""
Import samples
"""
from __future__ import print_function

from mongoengine import connect

from bson import json_util

from codado.tx import Main

from noms import recipe, user, DB_CONNECT, DB_NAME
from noms.const import ENCODING


class Sample(Main):
    """
    Load the .json sample files
    """
    synopsis = 'sample'

    def postOptions(self):
        connect(DB_NAME, DB_CONNECT)
        for cls in user.User, recipe.Recipe:
            cls.objects.delete()
            col = cls._get_collection()
            data = open('sample/%s.json' % col.name, encoding=ENCODING).read()
            col.insert_many(json_util.loads(data))
            print('{name}: {count} objects inserted'.format(
                name=col.name, count=cls.objects.count()
                ))
