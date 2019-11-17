"""
Tests of the shell scriptin bash subcommand
"""
import os
import re
import sys

from builtins import str

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
    os.chmod(fn, 0o770)


@fixture
def failScript(whiskDir):
    """
    Creates fail.whisk in whiskDir
    """
    fn = whiskDir('fail.whisk')
    open(fn, 'w').write(
            '#!/bin/bash\n# @@ synopsis: fake arg\nset -e\ngrep xyz abcxyz\n'
            )
    os.chmod(fn, 0o770)


def test_getMetadata(whiskDir, failScript):
    """
    Do I scan the file for yml strings and parse correctly?
    """
    pWhiskDir = patch.object(bash, 'WHISK_DIR', whiskDir)
    with pWhiskDir:
        cmd = bash.makeCommand('fail.whisk')()
        meta = cmd.getMetadata('fail.whisk')
    assert meta == {'synopsis': 'fake arg'}


def test_parseOptions(whiskDir, goodScript, capsys):
    """
    Do I run the bash command?

    Invokes the options parser directly, since BashCommand overrides it
    """
    pWhiskDir = patch.object(bash, 'WHISK_DIR', whiskDir)
    with pWhiskDir:
        cmd = bash.makeCommand('good.whisk')()
        cmd.parseOptions(['hello'])

    output, errput = capsys.readouterr()

    assert re.search('Running: .*good.whisk hello', output)
    assert re.search('hooray', output)


def test_postOptionsBad(whiskDir, failScript, capsys):
    """
    Do I fail when the bash command fails, and bring forward the error?

    Invokes the options parser directly, since BashCommand overrides it
    """
    pWhiskDir = patch.object(bash, 'WHISK_DIR', whiskDir)
    pArgv = patch.object(sys, 'argv', ['whisk', 'fail'])
    with pWhiskDir, pArgv:
        cmd = bash.makeCommand('fail.whisk')()
        with raises(CLIError) as e:
            cmd.parseOptions(['noo'])

    output, errput = capsys.readouterr()

    assert re.search(r'grep: abcxyz: No such file or directory', output)
    assert re.search(r'whisk exit 2: failed', str(e.value))
