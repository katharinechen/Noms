"""
Test the object that represents the config in the database
"""

from twisted.trial import unittest

from noms import config


class ConfigTest(unittest.TestCase):
    """
    Cover the Config document object
    """
    def test_appID(self):
        """
        Do I generate an appID from the apparentURL?
        """
        cfg = config.Config()
        self.assertEqual(cfg.appID, "https-app-nomsbook-com")
        cfg.apparentURL = ' https:/sadkflgfgddl-og45t.sadflg.dfs'
        self.assertEqual(cfg.appID, '-https-sadkflgfgddl-og45t-sadflg-dfs')
