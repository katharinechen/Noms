#!/usr/bin/env python
"""
Template a file using shell environment as the data
"""

import os
import sys

from jinja2 import Template


inputFile = open(sys.argv[1], 'rb')
tpl = Template(inputFile.read())
print tpl.render(**os.environ)
