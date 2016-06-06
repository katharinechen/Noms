"""
Test the command-line interface
"""
from twisted.trial import unittest

from noms import cli
from noms.test import mockConfig, REPLACE_DB_HOST


class CLITest(unittest.TestCase):
    def test_main(self):
        """
        Does main return a resource, suitable for starting up twisted web?
        """
        with mockConfig(cliOptions={'db': REPLACE_DB_HOST}):
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
