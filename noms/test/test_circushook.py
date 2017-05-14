"""
Tests of circushook, which runs before noms startup in a container
"""

from mock import patch

from pymongo.errors import ServerSelectionTimeoutError

from noms import circushook
from noms.whisk import  sample


def test_before_start_importSample(mockDatabase):
    """
    Do I attempt to load users when the database is available?
    """
    pSample = patch.object(sample, 'Sample', autospec=True)
    with pSample as mSample:
        ret = circushook.before_start_importSample(None, None, None)
    mSample.return_value.postOptions.assert_called_once_with()
    assert ret == True


def test_before_start_importSampleBadConnection(mockDatabase):
    """
    Do I return False when I can't find a database?
    """
    err = ServerSelectionTimeoutError
    pConnect = patch.object(circushook, 'connect', autospec=True, side_effect=err)
    with pConnect:
        ret = circushook.before_start_importSample(None, None, None)
    assert ret == False
