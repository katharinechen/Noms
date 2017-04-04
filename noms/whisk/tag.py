#!/usr/bin/env python
"""
Set a nomstag for this commit
"""
from __future__ import print_function

import json
from datetime import datetime

import attr

import git

from codado.tx import Main


REGION = 'us-west-2'
BUCKET = 'config.nomsbook.com'


def nowstring():
    """
    Produce an ISO-formatted UTC now string
    """
    return datetime.utcnow().isoformat()


@attr.s
class NomsTag(object):
    """
    A structured tag
    """
    message = attr.ib()
    tag = attr.ib()
    certbot_email = attr.ib(default=None)
    certbot_flags = attr.ib(default=None)
    created = attr.ib(default=nowstring)
    nomstag = attr.ib(default=True)


class Tag(Main):
    """
    Add a tag to the current git repo with JSON-structured data in the body
    """
    synopsis = "tag [options] <tag> [extra=args ...]"
    optParameters = [
            ['message', 'm', None, ''],
            ]

    def parseArgs(self, tag):
        """
        The tag name is required
        """
        self['tag'] = tag
        if not self['message']:
            self['message'] = self['tag']

    def postOptions(self):
        nt = NomsTag(
                message=self['message'],
                tag=self['tag'],
                )

        jsonNT = json.dumps({k: v for (k, v) in attr.asdict(nt).items() if v}, indent=2, sort_keys=1)
        repo = git.Repo('./')
        tag = repo.create_tag(self['tag'], message=jsonNT)

        print(tag, tag.tag.message)

