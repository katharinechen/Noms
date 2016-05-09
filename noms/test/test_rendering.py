"""
Test the facilities that support jinja rendering
"""
from inspect import cleandoc

from jinja2 import Template

from twisted.trial import unittest

from mock import patch

from noms.test import resetDatabase
from noms import rendering, config, secret


class HumanReadableTest(unittest.TestCase):
    """
    Cover the HumanReadable renderable object
    """

    def setUp(self):
        resetDatabase()
        config.Config().save()
        secret.put('auth0', 'auth0pub', 'auth0s3kr!t')
        self.tplString = cleandoc("""
            hi there
            {{ preload.apparentURL }}
            {{ preload.auth0Public }}
            {{ banana }}
        """)
        self.tplTemplate = Template(self.tplString)

    def test_render(self):
        """
        Do I produce a string using my template that uses all the variables I
        provided?
        """
        hrTemplate = rendering.HumanReadable(self.tplTemplate,
                banana='yellow and delicious')

        expected = cleandoc("""
            hi there
            https://app.nomsbook.com
            auth0pub
            yellow and delicious
            """)

        self.assertEqual(hrTemplate.render(None), expected)

        expected = cleandoc("""
            hi there
            https://app.nomsbook.com
            auth0pub
            brown and gross
            """)

        with patch.object(rendering.env, 'get_template', return_value=self.tplTemplate):
            hrString = rendering.HumanReadable('tpl_from_loader.txt',
                    banana='brown and gross')

            self.assertEqual(hrString.render(None), expected)

