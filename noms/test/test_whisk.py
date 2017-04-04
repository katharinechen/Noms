"""
Tests of the whisk top-level CLI
"""

from twisted.python import usage

from pytest import raises

from noms import whisk


def test_doc():
    """
    Does doc() extract a class's documentation?
    """
    class F(object):
        """
        This is a docstring.
        This is a second line.
        """

    assert whisk.doc(F) == "This is a docstring."


def test_noSubCommand():
    """
    If I'm invoked without a subCommand, do I error?
    """
    with raises(usage.UsageError):
        whisk.BaseWhisk().postOptions()
