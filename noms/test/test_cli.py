"""
Test the command-line interface
"""
from twisted.trial import unittest

from noms import cli, DBAlias
from noms.test import mockConfig


class CLITest(unittest.TestCase):
    def test_main(self):
        """
        Does main return a resource, suitable for starting up twisted web?
        """
        with mockConfig(cliOptions={'alias': DBAlias.nomsTest}):
            res = cli.main()
            self.assertTrue(hasattr(res, 'render'))

    def test_postOptions(self):
        """
        Does postOptions create the config and return options?
        """
        with mockConfig() as cfg:
            opts = cli.NomsOptions()
            opts['hax'] = 'haxor'
            opts.postOptions()
            self.assertEqual(cfg.cliOptions.get('hax'), 'haxor')
