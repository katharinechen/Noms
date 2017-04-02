#!/usr/bin/env python
"""
Import samples
"""
from __future__ import print_function

import shlex
import subprocess

from codado.tx import Main

from noms import NOMS_DB_HOST


class Sample(Main):
    """
    Load the .json sample files
    """
    synopsis = "** Usage: whisk sample"

    def postOptions(self):
        for filename in 'user', 'recipe':
            cl = shlex.split(
                "mongoimport -h %s --drop -d noms -c %s sample/%s.json" %
                (NOMS_DB_HOST, filename, filename)
                )
            print(subprocess.check_output(cl))
