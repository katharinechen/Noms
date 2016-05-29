"""
Test the command-line interface
"""
from twisted.trial import unittest
from twisted.internet import reactor

from mock import patch

from noms import cli
from noms.test import mockDatabase, mockConfig, REPLACE_DB_HOST


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
        with mockDatabase(), patch.object(reactor, 'run', autospec=True) as mReactorRun:
            opts = cli.NomsOptions()
            opts.postOptions()
            mReactorRun.assert_called_once_with()
