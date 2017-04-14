"""
Tests of the shell scriptin bash subcommand
"""
import os

from pytest import fixture, raises

from mock import patch

from codado.py import fromdir
from codado.tx import CLIError

from noms.whisk import bash


@fixture
def whiskDir(tmpdir):
    """
    A dir to put whisk scripts
    """
    wd = fromdir(str(tmpdir), 'whisk')
    os.mkdir(wd())
    return wd


@fixture
def goodScript(whiskDir):
    """
    Creates good.whisk in whiskDir
    """
    fn = whiskDir('good.whisk')
    open(fn, 'w').write(
            '#!/bin/bash\n# @@ synopsis: good arg\necho "hooray"\n'
            )
    os.chmod(fn, 0770)


@fixture
def failScript(whiskDir):
    """
    Creates fail.whisk in whiskDir
    """
    fn = whiskDir('fail.whisk')
    open(fn, 'w').write(
            '#!/bin/bash\n# @@ synopsis: fake arg\nset -e\nfalse\n'
            )
    os.chmod(fn, 0770)


def test_getMetadata(whiskDir, failScript):
    """
    Do I scan the file for yml strings and parse correctly?
    """
    pWhiskDir = patch.object(bash, 'WHISK_DIR', whiskDir)
    with pWhiskDir:
        cmd = bash.makeCommand('fail.whisk')()
        meta = cmd.getMetadata('fail.whisk')
    assert meta == {'synopsis': 'fake arg'}


def test_parseOptions(whiskDir, goodScript):
    pWhiskDir = patch.object(bash, 'WHISK_DIR', whiskDir)
    with pWhiskDir:
        cmd = bash.makeCommand('good.whisk')()
        cmd.parseOptions(['hello'])
    assert 0


def test_postOptionsBad(whiskDir, failScript):
    pWhiskDir = patch.object(bash, 'WHISK_DIR', whiskDir)
    with pWhiskDir:
        cmd = bash.makeCommand('fail.whisk')()
        with raises(CLIError) as e:
            cmd.parseOptions(['noo'])
    assert str(e) == 'nooooo'
