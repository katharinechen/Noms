"""
Test the facilities that support jinja rendering
"""
import json
from inspect import cleandoc

from jinja2 import Template

from twisted.trial import unittest

from mongoengine import StringField, IntField

from mock import patch

from noms.test import mockConfig, mockDatabase
from noms import rendering, secret, recipe, urlify


class HumanReadableTest(unittest.TestCase):
    """
    Cover the HumanReadable renderable object
    """
    @mockConfig()
    def test_render(self):
        """
        Do I produce a string using my template that uses all the variables I
        provided?
        """
        pubkey, seckey = secret.get('auth0')
        self.assertEqual((pubkey, seckey), ('abc123', 'ABC!@#'))
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
            abc123
            yellow and delicious
            """)

        self.assertEqual(hrTemplate.render(None), expected)

        expected = cleandoc("""
            hi there
            https://app.nomsbook.com
            abc123
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
    @mockConfig()
    def test_empty(self):
        """
        Do I correctly produce an error for empty queries?
        """
        qs = recipe.Recipe.objects()
        rqs = rendering.RenderableQuerySet(qs)
        self.assertRaises(rendering.EmptyQuery, rqs.render, None)

    @mockConfig()
    def test_render(self):
        """
        Do I produce a json array from a query?
        """
        author = u'cory'
        url = urlify(u'delicious sandwich', author)
        recipe.Recipe(name=u'delicious sandwich', author=author, urlKey=url).save()
        url = urlify(u'delicious soup', author)
        recipe.Recipe(name=u'delicious soup', author=author, urlKey=url).save()

        qs = recipe.Recipe.objects()
        expected = '[{"recipeYield": null, "tags": [], "name": "delicious sandwich", "author": "cory", "instructions": [], "ingredients": [], "urlKey": "delicious-sandwich-cory-", "user": "katharinechen.ny@gmail.com"}, {"recipeYield": null, "tags": [], "name": "delicious soup", "author": "cory", "instructions": [], "ingredients": [], "urlKey": "delicious-soup-cory-", "user": "katharinechen.ny@gmail.com"}]'
        self.assertEqual(rendering.RenderableQuerySet(qs).render(None), expected)


class RenderableDocumentTest(unittest.TestCase):
    @mockDatabase()
    def test_safe(self):
        class Doc(rendering.RenderableDocument):
            pass

        self.assertRaises(NotImplementedError, Doc().safe)

    @mockDatabase()
    def test_render(self):
        class Doc(rendering.RenderableDocument):
            safeValue = StringField()
            badValue = StringField()
            intValue = IntField()

            def safe(self):
                return {'safe': self.safeValue, 'int': self.intValue}

        doc = Doc(safeValue='good', badValue='no', intValue=12)
        self.assertEqual(doc.render(None),
                json.dumps({'safe': 'good', 'int': 12})
                )
