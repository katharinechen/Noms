"""
Test the command-line interface
"""
import subprocess  

from mock import patch

from noms import cli


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
    pSubprocess = patch.object(subprocess, 'Popen', return_value="called!")
    bashCommand = "sass --watch static/scss/base.scss:static/css/base.css --trace".split()

    with pSubprocess as mSubprocess: 
        opts = cli.NomsOptions()
        opts['hax'] = 'haxor'
        opts.postOptions()
        mSubprocess.assert_called_once_with(bashCommand, stdout=-1)
        assert mockConfig.cliOptions.get('hax') == 'haxor'
