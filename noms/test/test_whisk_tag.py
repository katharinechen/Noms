"""
Tests of `whisk tag`
"""
import json
from datetime import datetime

import git

from pytest import fixture

from mock import patch, create_autospec, MagicMock

from noms.whisk import tag


def test_parseArgs():
    """
    Do I interpret command-line args correctly
    """
    tt = tag.Tag()
    tt.parseArgs('hello')
    assert tt['message'] == tt['tag'] == 'hello'
    tt['message'] = 'goodbye'
    tt.parseArgs('hello')
    assert tt['message'] == 'goodbye'
    assert tt['tag'] == 'hello'


@fixture
def gitRepo():
    """
    Return a git repo that returns a known value for `create_tag`
    """
    obj = create_autospec(git.Repo)
    def _create_tag(tagName, message):
        mockTag = create_autospec(git.Tag)
        mockTag.__str__ = MagicMock(return_value=tagName)
        mockTag.tag.message = message
        return mockTag

    obj.return_value.create_tag = MagicMock(side_effect=_create_tag)
    return obj



def test_postOptions(gitRepo, capsys):
    """
    Do I make a call to git to save the right tag with the right data?
    """
    tt = tag.Tag()
    tt['tag'] = tt['message'] = 'hello-world'
    pRepo = patch.object(git, 'Repo', gitRepo)
    pNowstring = patch.object(datetime.utcnow.return_value, 'isoformat',
            return_value="2017-04-04T16:41:41.584844")
    with pRepo as mRepo, pNowstring:
        tt.postOptions()

    expectedJSON = json.dumps({
              "created": "2017-04-04T16:41:41.584844",
              "message": "hello-world",
              "nomstag": True,
              "tag": "hello-world"
            }, indent=2, sort_keys=1)
    mRepo.return_value.create_tag.assert_called_once_with(
            'hello-world',
            message=expectedJSON)
    out, err = capsys.readouterr()
    assert out == 'hello-world' + expectedJSON
