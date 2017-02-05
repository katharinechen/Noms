"""
Test the command-line interface
"""
import subprocess

from noms import cli, secret

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
    # remove the localapi secret that mockConfig creates, so we can be sure
    # postOptions will recreate it.
    secret.SecretPair.objects.get(name='localapi').delete()

    opts = cli.NomsOptions()
    opts['hax'] = 'haxor'
    pPopen = patch.object(subprocess, 'Popen', autospec=True)
    with pPopen as mPopen:
        opts.postOptions()
        args = mPopen.call_args_list[0]
        assert args[0][0][0] == 'watchmedo'
    assert mockConfig.cliOptions.get('hax') == 'haxor'

    # did postOptions recreate the localapi secret?
    assert secret.get('localapi')[0] == 'localapi'
