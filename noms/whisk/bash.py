"""
Whisk subcommands implemented as shell scripts.
"""
from __future__ import print_function

import pipes
import re
from subprocess import Popen, PIPE, STDOUT
import sys

import yaml

from codado.tx import Main, CLIError
from codado.py import fromdir

from noms.const import ENCODING


WHISK_DIR = fromdir(__file__)


class BashCommand(Main):
    """
    A command-line program implemented as a shell script
    """
    @classmethod
    def getMetadata(cls, filename):
        """
        Parse comment lines containing '@@' for yaml metadata, such as
        synopsis
        """
        data = {}
        for line in open(WHISK_DIR(filename)):
            if re.match(r'^\s*#\s*@@', line):
                ymlText = line[line.index('@@')+2:].strip()
                data.update(yaml.load(ymlText))
        return data

    def postOptions(self):
        """
        Run the command I'm wrapped around, displaying the ouptut
        """
        cmd = [WHISK_DIR(self.path)] + (self.rawArgs if self.rawArgs else [])
        print("Running: %r" % ' '.join(pipes.quote(x) for x in cmd))
        proc = Popen(cmd, stderr=STDOUT, stdout=PIPE, bufsize=1, encoding=ENCODING)
        while True: # this is weird, workaround to a bug in Popen that
            # makes stdout block instead of giving us data line by line
            line = proc.stdout.readline()
            if not line:
                break
            sys.stdout.write(line)

        proc.wait()
        if not proc.returncode == 0:
            raise CLIError(sys.argv[0], proc.returncode, 'failed')

    def parseOptions(self, args):
        self.rawArgs = args
        self.postOptions()


def makeCommand(scriptName):
    def BashMaker():
        self = BashCommand()
        self.synopsis = self.getMetadata(scriptName)['synopsis']
        self.path = WHISK_DIR(scriptName)
        return self

    BashMaker.__name__ = scriptName.split('.whisk')[0].capitalize()

    return BashMaker
