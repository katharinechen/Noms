#!/usr/bin/env python
"""
Output the environment variables sourced by build shell scripts
"""
from __future__ import print_function

from inspect import cleandoc
from io import StringIO
import json
import os
import pipes
import re

from future import standard_library
standard_library.install_aliases()
from builtins import str, object

import attr

from git import Repo

from codado.tx import Main, CLIError


LOCAL_ENV = 'local.env'


def readEnvironmentFile(fl):
    """
    Read a docker-style environment file

    This file must consist of K=V lines with optional #comment lines.
    """
    ret = {}
    if os.path.exists(fl):
        for line in open(fl):
            if re.match(r'^\s*#', line):
                continue
            k, v = line.strip().split('=', 1)
            ret[k] = v
    return ret


def parseDescribe(s):
    """
    Attempt to extract tag name and data from the describe string
    """
    s = s.strip()
    # some sanity checks on describe string
    if re.match(r'^(.*/){2}', s):
        s = cleandoc("""
            ** Invalid NOMS_VERSION=%r
            ** You should build from either the HEAD of this branch or a tagged revision
            """ % s)
        raise ValueError(s)

    short = s.split('/', 1)[1] if '/' in s else s
    a, b, c = short.rsplit('-', 2)
    return dict(
            short=short,
            name=a,
            count=b,
            abbrev=c[1:] # strip the "g"
            )


@attr.s
class Description(object):
    """
    A structured set of parameters to become the build environment
    """
    NOMS_VERSION = attr.ib(default=('cli', None))
    NOMS_DB_HOST = attr.ib(default=('cli', 'mongo'))
    certbot_flags = attr.ib(default=('cli', ''))
    certbot_email = attr.ib(default=('cli', 'corydodt@gmail.com'))
    public_hostname = attr.ib(default=('cli', 'dev.nomsbook.com'))
    proxy_hostname = attr.ib(default=('cli', 'noms-main'))
    proxy_port = attr.ib(default=('cli', '8080'))

    @classmethod
    def build(cls, opts=None):
        """
        Contruct a new Description from environment and options
        """
        if opts is None:
            opts = {}

        repo = Repo('./')

        described = repo.git.describe(['--all', '--long'])
        parsed = parseDescribe(described)

        # 1. command-line params
        self = cls(**{k: ('cli', v) for (k, v) in opts.items()})

        # 2. git describe
        self.NOMS_VERSION = ('git describe', parsed['short'])

        # 3. local.env
        local = readEnvironmentFile(LOCAL_ENV)
        for k, v in local.items():
            setattr(self, k, ('local.env', v))

        # 4. os.environ
        for k in attr.asdict(self):
            v = os.environ.get(k, None)
            if v is not None:
                setattr(self, k, ('process environment', v))

        # 5. structured nomstag
        try:
            mess = os.environ.get('TRAVIS_COMMIT_MESSAGE', '')
            loaded = json.loads(mess)
            if 'nomstag' in loaded:
                for k, v in loaded.items():
                    setattr(self, k, ('nomstag', v))
            else:
                raise ValueError("JSON-like commit body was not a nomstag")
        except ValueError:
            "Not a structured tag"

        return self

    @classmethod
    def asParameters(cls):
        """
        Return the 4-tuples that can be used as Options optParameters
        """
        ret = []
        atts = attr.fields(cls)
        for att in atts:
            ret.append((att.name, None, att.default[1], ''))
        return ret

    def asEnvironment(self):
        """
        Produce a shell environment from me, as a string
        """
        out = StringIO()
        env = attr.asdict(self)
        last = ''
        for src, k, v in sorted((str(src), k, v) for (k, (src, v)) in env.items()):
            if last != src:
                last = src
                print(u'\n# from', src, file=out)
            print(u'%s=%s' % (k, pipes.quote(str(v)) if v else u''), file=out)
        return out.getvalue()


class Describe(Main):
    """
    Describe the build environment of the current directory, using 5 data sources

    1. command-line parameters;
    2. stdin; which is assumed to be coming from `git describe --all --long`
    3. the file local.env;
    4. the process environment variables;
    5. the json data loaded from the git tag, if any such JSON data exists

    This data is prioritized from last to first; so JSON data is used, unless
    it is missing; then environment variables unless they are missing; then
    local.env unless it is missing; then git describe; then
    command-line parameters or their defaults.
    """
    synopsis = "describe"
    optParameters = Description.asParameters()

    def postOptions(self):
        try:
            description = Description.build(self)
        except ValueError as e: # pragma: nocover
            raise CLIError('whisk describe', 1, e.message)
        print(description.asEnvironment())
