"""
Tests of `whisk sample`
"""
import subprocess

from mock import patch, call

from noms.whisk import sample


def test_postOptions():
    """
    Do I invoke mongoimport on all these files
    """
    ss = sample.Sample()
    pCheckOutput = patch.object(subprocess, 'check_output', autospec=True)
    with pCheckOutput as mCheckOutput:
        ss.postOptions()

    assert mCheckOutput.call_args_list == [
        call([
            'mongoimport', '-h', sample.NOMS_DB_HOST, '--drop', '-d', 'noms',
            '-c', 'user', 'sample/user.json']),
        call([
            'mongoimport', '-h', sample.NOMS_DB_HOST, '--drop', '-d', 'noms',
            '-c', 'recipe', 'sample/recipe.json']),
        ]
