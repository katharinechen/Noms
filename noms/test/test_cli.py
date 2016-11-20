"""
Test the command-line interface
"""
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
    opts = cli.NomsOptions()
    opts['hax'] = 'haxor'
    opts.postOptions()
    assert mockConfig.cliOptions.get('hax') == 'haxor'
