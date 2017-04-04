"""
Tests of `whisk tag`
"""
import os
from inspect import cleandoc
import json

import attr

import git

from pytest import fixture, raises

from mock import patch, create_autospec, MagicMock

from noms.whisk import tag


