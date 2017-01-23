"""
Test the command-line interface
"""
import subprocess

from noms import cli

from mock import patch


def test_main(mockConfig):
    """
    Does main return a resource, suitable for starting up twisted web?
    """
    res = cli.main()
    assert hasattr(res, 'render')


def test_postOptions(mockConfig):
    """
    Does postOptions create the config and return options?
    """
    opts = cli.NomsOptions()
    opts['hax'] = 'haxor'
    pPopen = patch.object(subprocess, 'Popen', autospec=True)
    with pPopen as mPopen:
        opts.postOptions()
        args = mPopen.call_args_list[0]
        assert args[0][0][0] == 'watchmedo'
    assert mockConfig.cliOptions.get('hax') == 'haxor'
