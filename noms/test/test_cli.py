"""
Test the command-line interface
"""
import subprocess

from mock import patch

from noms import cli, secret


def test_main(mockConfig):
    """
    Does main return a resource, suitable for starting up twisted web?
    """
    res = cli.main()
    assert hasattr(res, 'render')


def test_postOptions(mockConfig):
    """
    Does postOptions create the configuration and return options?
    """
    # remove the localapi secret that mockConfig creates, so we can be sure
    # postOptions will recreate it.
    secret.SecretPair.objects.get(name='localapi').delete()

    opts = cli.Run()
    opts['hax'] = 'haxor'
    pPopen = patch.object(subprocess, 'Popen', autospec=True)

    with pPopen as mPopen:
        opts.postOptions()

    calls = mPopen.call_args_list
    assert calls[0][0][0][0] == 'watchmedo'
    assert calls[1][0][0][:3] == ['bundle', 'exec', 'sass']
    assert mockConfig.cliOptions.get('hax') == 'haxor'

    # did postOptions recreate the localapi secret?
    assert secret.get('localapi')[0] == 'localapi'
