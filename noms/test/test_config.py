"""
Test the object that represents the config in the database
"""

from noms import configuration


def test_appID():
    """
    Do I generate an appID from the apparentURL?
    """
    cfg = configuration.Configuration()
    assert cfg.appID == "https-app-nomsbook-com"
    cfg.apparentURL = ' https:/sadkflgfgddl-og45t.sadflg.dfs'
    assert cfg.appID == '-https-sadkflgfgddl-og45t-sadflg-dfs'
