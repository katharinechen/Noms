# vim:fileencoding=utf-8
"""
Test of package-level code contained in noms.__init__
"""

from twisted.trial import unittest

from noms import urlify, LazyConfig
from noms.test import ConfigMock


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
        self.configMocker = ConfigMock()
        self.config = LazyConfig()

    def tearDown(self):
        self.configMocker.finish()

    def test_laziness(self):
        """
        Do I acquire a config object upon access?
        """
        self.assertFalse('_realConfig' in self.config.__dict__,
                "oops, test config has _realConfig prematurely")
        self.config.apparentURL
        self.assertTrue('_realConfig' in self.config.__dict__,
                "oops, test config should have _realConfig now but doesn't")

    def test_attributeAccess(self):
        """
        Try out the attribute proxying properties
        """
        self.assertFalse('_realConfig' in self.config.__dict__,
                "oops, test config has _realConfig prematurely")
        self.assertRaises(TypeError,
                setattr, self.config, 'uninitialized', 20)
        self.assertEqual(self.config.apparentURL, 'https://app.nomsbook.com')
        self.config.apparentURL = 'dfgkljdhf'
        self.assertEqual(self.config.apparentURL, 'dfgkljdhf')
