#!/usr/bin/env python
"""
I used this script to dump an existing secret collection to kubernetes
"""

from __future__ import print_function

import click

from twisted.internet import task, defer

from noms import secret
from mongoengine import connect


@click.command()
def savesecrets():
    task.react(main)


@defer.inlineCallbacks
def main(reactor):
    connect("noms")
    for sec in secret.SecretPair.objects():
        print(sec.name)
        res = yield sec.putK8s()
        print(res)

    yield None


if __name__ == '__main__':
    savesecrets()
