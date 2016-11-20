"""
Test the facilities that support jinja rendering
"""
import json
from inspect import cleandoc

from jinja2 import Template

from twisted.trial import unittest

from py.test import raises 

from mongoengine import StringField, IntField

from mock import patch

from noms.test import mockConfig, mockDatabase
from noms import rendering, secret, recipe, urlify, user


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
        
        u = user.User(email="dude@gmail.com")
        u.save()

        url = urlify(u'delicious sandwich', author)
        recipe.Recipe(name=u'delicious sandwich', author=author, urlKey=url, user=u).save()
        url = urlify(u'delicious soup', author)
        recipe.Recipe(name=u'delicious soup', author=author, urlKey=url, user=u).save()

        qs = recipe.Recipe.objects()
        expected = [
                {"recipeYield": None, "tags": [], "name": "delicious sandwich", "author": "cory", "instructions": [], "ingredients": [], "urlKey": "delicious-sandwich-cory-", "user": {"roles": [], "givenName": None, "email": "dude@gmail.com", "familyName": None}},
                {"recipeYield": None, "tags": [], "name": "delicious soup", "author": "cory", "instructions": [], "ingredients": [], "urlKey": "delicious-soup-cory-", "user": {"roles": [], "givenName": None, "email": "dude@gmail.com", "familyName": None}}]
        expected = json.dumps(expected, sort_keys=True)
        assert rendering.RenderableQuerySet(qs).render(None) == expected


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
                json.dumps({'safe': 'good', 'int': 12}, sort_keys=True)
                )


# this is in the style of py.test 
def test_resourceEncoder():
    """
    Test that json encoder works on our objects 
    """
    class SafeClass(object): 
        def safe(self):
            return "19"
    ret = json.dumps(SafeClass(), cls=rendering.ResourceEncoder)
    assert ret == '"19"'

    class NotSoSafeClass(object): 
        pass 

    with raises(TypeError): 
        json.dumps(NotSoSafeClass(), cls=rendering.ResourceEncoder)
