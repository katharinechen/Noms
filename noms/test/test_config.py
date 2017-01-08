"""
Test the object that represents the config in the database
"""

from noms import config


def test_appID():
    """
    Do I generate an appID from the apparentURL?
    """
    cfg = config.Config()
    assert cfg.appID == "https-app-nomsbook-com"
    cfg.apparentURL = ' https:/sadkflgfgddl-og45t.sadflg.dfs'
    assert cfg.appID == '-https-sadkflgfgddl-og45t-sadflg-dfs'
