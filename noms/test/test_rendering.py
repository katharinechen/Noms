"""
Test the facilities that support jinja rendering
"""
from inspect import cleandoc

from jinja2 import Template

from twisted.trial import unittest

from mock import patch

from noms.test import mockConfig
from noms import rendering, secret, recipe, urlify


class HumanReadableTest(unittest.TestCase):
    """
    Cover the HumanReadable renderable object
    """
    def test_render(self):
        """
        Do I produce a string using my template that uses all the variables I
        provided?
        """
        with mockConfig():
            secret.put('auth0', 'auth0pub', 'auth0s3kr!t')
            self.tplString = cleandoc("""
                hi there
                {{ preload.apparentURL }}
                {{ preload.auth0Public }}
                {{ banana }}
            """)
            self.tplTemplate = Template(self.tplString)

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


class RenderableQuerySetTest(unittest.TestCase):
    """
    Cover the RenderableQuerySet
    """
    def test_render(self):
        """
        Do I produce a json array from a query?
        """
        with mockConfig():
            author = u'cory'
            url = urlify(u'delicious sandwich', author)
            recipe.Recipe(name=u'delicious sandwich', author=author, urlKey=url).save()
            url = urlify(u'delicious soup', author)
            recipe.Recipe(name=u'delicious soup', author=author, urlKey=url).save()

            qs = recipe.Recipe.objects()
            expected = '[{"recipeYield": null, "tags": [], "name": "delicious sandwich", "author": "cory", "instructions": [], "ingredients": [], "urlKey": "delicious-sandwich-cory-", "user": "katharinechen.ny@gmail.com"}, {"recipeYield": null, "tags": [], "name": "delicious soup", "author": "cory", "instructions": [], "ingredients": [], "urlKey": "delicious-soup-cory-", "user": "katharinechen.ny@gmail.com"}]'
            self.assertEqual(rendering.RenderableQuerySet(qs).render(None), expected)
