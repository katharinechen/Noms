"""
Test the facilities that support jinja rendering
"""
import json
from inspect import cleandoc

from builtins import object

from jinja2 import Template

from pytest import raises

from mongoengine import StringField, IntField

from mock import patch

import noms
from noms import recipe, rendering, secret, urlify, user


def test_renderHumanReadable(mockConfig):
    """
    Do I produce a string using my template that uses all the variables I
    provided?
    """
    pubkey, seckey = secret.get('auth0')
    assert (pubkey, seckey) == ('abc123', 'ABC!@#')
    tplString = cleandoc("""
        hi there
        {{ preload.apparentURL }}
        {{ preload.auth0Public }}
        {{ banana }}
    """)
    tplTemplate = Template(tplString)

    pCONFIG = patch.object(noms, 'CONFIG', mockConfig)
    with pCONFIG:
        hrTemplate = rendering.HumanReadable(tplTemplate,
                banana='yellow and delicious')

    expected = cleandoc("""
        hi there
        https://app.nomsbook.com
        abc123
        yellow and delicious
        """)

    with pCONFIG:
        assert hrTemplate.render(None) == expected

    expected = cleandoc("""
        hi there
        https://app.nomsbook.com
        abc123
        brown and gross
        """)

    pGetTemplate = patch.object(rendering.env, 'get_template', return_value=tplTemplate)
    with pGetTemplate, pCONFIG:
        hrString = rendering.HumanReadable('tpl_from_loader.txt',
                banana='brown and gross')

        assert hrString.render(None) == expected


def test_renderRenderableQuerySet(mockConfig):
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
    expected = json.dumps([
        {"recipeYield": None, "tags": [], "name": "delicious sandwich", "author": "cory", "instructions": [], "ingredients": [], "urlKey": "delicious-sandwich-cory", "user": {"roles": [], "givenName": None, "email": "dude@gmail.com", "familyName": None}},
        {"recipeYield": None, "tags": [], "name": "delicious soup", "author": "cory", "instructions": [], "ingredients": [], "urlKey": "delicious-soup-cory", "user": {"roles": [], "givenName": None, "email": "dude@gmail.com", "familyName": None}}
    ], sort_keys=True)
    assert rendering.RenderableQuerySet(qs).render(None) == expected


def test_safe(mockDatabase):
    class Doc(rendering.RenderableDocument):
        pass

    with raises(NotImplementedError):
        Doc().safe()


def test_render(mockDatabase):
    class Doc(rendering.RenderableDocument):
        safeValue = StringField()
        badValue = StringField()
        intValue = IntField()

        def safe(self):
            return {'safe': self.safeValue, 'int': self.intValue}

    doc = Doc(safeValue='good', badValue='no', intValue=12)
    assert doc.render(None) == json.dumps({'safe': 'good', 'int': 12}, sort_keys=True)


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


def test_responseData():
    """
    Test that json encoder works on ResponseData structures
    """
    ret = rendering.OK().render(None)
    assert ret == '{"status": "ok", "message": ""}'

    ret = rendering.ERROR(message="ono!").render(None)
    assert ret == '{"status": "error", "message": "ono!"}'
