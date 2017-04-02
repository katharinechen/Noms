#!/usr/bin/env python
"""
Set a nomstag for this commit
"""
from __future__ import print_function

import json
from datetime import datetime

import git

from codado.tx import Main


REGION = 'us-west-2'
BUCKET = 'config.nomsbook.com'


class Tag(Main):
    """
    Add a tag to the current git repo with JSON-structured data in the body
    """
    synopsis = "** Usage: noms-tag -m 'blah blah' <tag> [extra=args ...]"
    optParameters = [
            ['message', 'm', None, ''],
            ['define', 'D', None, ''],
            ]

    def opt_define(self, value):
        k, v = value.split("=")
        self.setdefault('extra', {})[k] = v

    def parseArgs(self, tag):
        """
        The tag name is required
        """
        self.setdefault('extra', {})
        self['created'] = datetime.utcnow().isoformat()
        self['tag'] = tag
        if not self['message']:
            self['message'] = self['tag']

    def postOptions(self):
        data = dict(
                nomstag=True,
                created=self['created'],
                message=self['message'],
                tag=self['tag'],
                **self['extra']
                )
        jdata = json.dumps(data, indent=2, sort_keys=1)
        repo = git.Repo('./')
        tag = repo.create_tag(self['tag'], message=jdata)

        print(tag, tag.tag.message)

