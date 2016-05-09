# vim:fileencoding=utf-8
"""
Test of code contained in noms.__init__
"""

from twisted.trial import unittest

from noms import urlify, LazyConfig


class FnTest(unittest.TestCase):
    """
    Coverage of functions in __init__
    """
    def test_urlify(self):
        """
        Do I produce punycode output for the inputs?
        """
        helloThere = u'你好'
        self.assertEqual(urlify(u'asdf', helloThere, u'69'),
                'asdf--69-nm2mf94f')


class LazyConfigTest(unittest.TestCase):
    """
    Coverage of LazyConfig
    """
    def setUp(self):
        self.config = LazyConfig()

    def test_laziness(self):
        """
        Do I acquire a config object upon access?
        """
        1/0

    def test_dictLike(self):
        """
        Try out the dict-like properties
        """
        1/0
