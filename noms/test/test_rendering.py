"""
Test the facilities that support jinja rendering
"""
from inspect import cleandoc

from jinja2 import Template

from twisted.trial import unittest

from noms.test import dbutil
from noms import rendering


class HumanReadableTest(unittest.TestCase):
    """
    Cover the HumanReadable renderable object
    """

    def setUp(self):
        self.tplString = cleandoc("""
            hi there
            {{ preload.apparentURL }}
            {{ preload.auth0Public }}
            {{ banana }}
        """)
        self.tplTemplate = Template(self.tplString)
        self.tplFilename = 'human_readable_test.txt'
        tplf = open(self.tplFilename, 'w')
        tplf.write(self.tplString)

    def test_render(self):
        """
        Do I produce a string using my template that uses all the variables I
        provided?
        """
        hrTemplate = rendering.HumanReadable(self.tplTemplate,
                banana='yellow and delicious')

        expected = cleandoc("""
            hi there
            foo-apparent-url-443
            32408y3hfsdkf
            yellow and delicious
            """)

        self.assertEqual(hr.render(None), expected)

        hrString = rendering.HumanReadable(self.tplFilename,
                banana='brown and gross')

        expected = cleandoc("""
            hi there
            foo-apparent-url-443
            32408y3hfsdkf
            brown and gross
            """)

        self.assertEqual(hr.render(None), expected)

