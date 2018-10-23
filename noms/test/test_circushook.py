"""
Tests of circushook, which runs before noms startup in a container
"""

from mock import patch

from pymongo.errors import ServerSelectionTimeoutError

from noms import circushook, whisk


def test_before_start_importSample(mockConfig):
    """
    Do I attempt to load users when the database is available?
    """
    pWhisk = patch.object(whisk, 'BaseWhisk', autospec=True)
    with pWhisk as mWhisk:
        ret = circushook.before_start(None, None, None)
    mWhisk.main.assert_called_once_with(['sample'])
    assert ret == True


def test_before_start_importSampleBadConnection(mockConfig):
    """
    Do I return False when I can't find a database?
    """
    err = ServerSelectionTimeoutError
    pConnect = patch.object(circushook, 'connect', autospec=True, side_effect=err)
    with pConnect:
        ret = circushook.before_start(None, None, None)
    assert ret == False
