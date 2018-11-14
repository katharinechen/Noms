"""
Tests of noms.server, mostly handlers
"""
import json
import re

from twisted.web.test.requesthelper import DummyRequest
from twisted.python.components import registerAdapter
from twisted.internet import defer

import treq

from werkzeug.exceptions import Forbidden

from klein.app import KleinRequest
from klein.interfaces import IKleinRequest

from mock import patch, ANY

from pytest import fixture, inlineCallbacks, raises

from crosscap.testing import EZServer

from noms import (
        server, fromNoms,
        recipe, urlify, CONFIG,
        )
from noms.interface import ICurrentUser
from noms.user import User
from noms.rendering import ResponseStatus as RS, OK, ERROR
from noms.test.conftest import request, requestJSON


# klein adapts Request to KleinRequest internally when the Klein() object
# begins handling a request. This isn't explicitly done for DummyRequest
# (because this is an object that only appears in tests), so we create our own
# adapter -- now we can use DummyRequest wherever a Klein() object appears in
# our code
registerAdapter(KleinRequest, DummyRequest, IKleinRequest)
registerAdapter(User.fromRequest, DummyRequest, ICurrentUser)


def test_querySet(mockConfig):
    """
    Does querySet(fn)() render the result of the cursor returned by fn?
    """
    def _configs(req):
        return User.objects()

    User(email='hello').save()
    configsFn = server.querySet(_configs)
    assert configsFn(None) == b'[{"email": "hello", "familyName": null, "givenName": null, "roles": []}]'


@fixture
def rootServer():
    """
    Instance of EZServer using the server.Server routes
    """
    return EZServer(server.Server)


@fixture
def apiServer():
    """
    Instance of EZServer using the server.APIServer routes
    """
    return EZServer(server.APIServer)


@fixture
def req():
    """
    Basic empty request
    """
    return request([])


@fixture
def reqJS():
    """
    Basic empty request that uses JSON request wrapping/unwrapping
    """
    return requestJSON([])


@inlineCallbacks
def test_static(mockConfig, rootServer, capsys):
    """
    Does /static/ return a FilePath?
    """
    with fromNoms:
        # first try without the hash
        r = yield rootServer.handler('static', postpath=[
            b'js', b'app.js'])
        assert 'app.js' in r.child('js').listdir()
        out, err = capsys.readouterr()
        assert out.startswith('WARNING:')

        # now try with the hash, should get the same result
        r = yield rootServer.handler('static', postpath=[
            b'HASH-hello-my-dolly', b'js', b'app.js'])
        assert 'app.js' in r.child('js').listdir()


@inlineCallbacks
def test_index(mockConfig, rootServer, req):
    """
    Does / return the home page?
    """
    r = yield rootServer.handler('index', req)
    assert re.search(rb'<title>NOM NOM NOM</title>', r.render(req))


@inlineCallbacks
def test_showRecipes(mockConfig, rootServer, req):
    """
    Does /recipes list recipes?
    """
    r = yield rootServer.handler('showRecipes', req)
    assert re.search(rb'partials/recipe-list.html', r.render(req))


@inlineCallbacks
def test_createRecipe(mockConfig, rootServer, req):
    """
    Does /recipes/new show the creation page?
    """
    r = yield rootServer.handler('createRecipe', req)
    assert re.search(rb'partials/recipe-create.html', r.render(req))


@inlineCallbacks
def test_showRecipe(mockConfig, rootServer, req):
    """
    Does /recipes/xxx show recipe xxx?
    """
    r = yield rootServer.handler('showRecipe', req, 'foo-gmail-com-honeyed-cream-cheese-pear-pie-')
    rendered = r.render(req)
    assert re.search(rb'partials/recipe-read.html', rendered)
    assert re.search(rb'nomsPreload.*urlKey.*foo-gmail-com-honeyed-cream-cheese-pear-pie-',
        rendered)


@inlineCallbacks
def test_api(mockConfig, rootServer, req):
    """
    Do I get the /api/ subtree when I access a URL?
    """
    res = yield rootServer.handler("api")
    assert 'recipeList' in res._app.endpoints


@fixture
def recipes():
    """
    Set up some recipes explicitly during a test
    """
    author = u'cory'
    url = urlify(u'weird sandwich', author)
    r1 = recipe.Recipe(name=u'weird sandwich', author=author, urlKey=url).save()
    url = urlify(u'weird soup', author)
    r2 = recipe.Recipe(name=u'weird soup', author=author, urlKey=url).save()
    return (r1, r2)


@inlineCallbacks
def test_getRecipe(mockConfig, apiServer, recipes, reqJS):
    """
    Does /api/recipe/.... return a specific recipe?
    """
    r = yield apiServer.handler('getRecipe', reqJS, 'weird-soup-cory')
    assert r['name'] == 'weird soup'


@inlineCallbacks
def test_saveRecipe(mockConfig, apiServer, weirdo, recipes):
    """
    Does /api/recipe/urlKey/save ... save a specific recipe?
    """
    content = dict(
            name='Weird soup',
            author='Weird Soup Man',
            ingredients=['weirdness', 'soup'],
            instructions=['mix together ingredients', 'heat through'],
            )
    reqJS = requestJSON([], content=content)
    resp = yield apiServer.handler('saveRecipe', reqJS, urlKey='weird-sandwich-cory-')
    assert resp == OK()

@inlineCallbacks
def test_deleteRecipe(mockConfig, apiServer, reqJS, recipes):
    """
    Does /api/recipe/urlKey/delete... delete a specific recipe?
    """
    # Error: recipe does not exist
    resp = yield apiServer.handler('deleteRecipe', reqJS, urlKey="stuff")
    assert resp == ERROR(message="Recipe not found")

    # Success: recipe exists
    resp = yield apiServer.handler('deleteRecipe', reqJS, urlKey='weird-sandwich-cory-')
    assert resp == OK()


@inlineCallbacks
def test_recipeList(mockConfig, apiServer, recipes):
    """
    Does /api/recipe/list return a structured list of recipes from the database?
    """
    r = json.loads((yield apiServer.handler('recipeList')))
    keys = [x['urlKey'] for x in r]
    assert keys == ['weird-sandwich-cory', 'weird-soup-cory']


@inlineCallbacks
def test_user(mockConfig, apiServer, weirdo):
    """
    Does /api/user return the current user?
    """
    req = requestJSON([], session_user=weirdo)
    r = yield apiServer.handler('user', req)
    assert r.email == 'weirdo@gmail.com'


@inlineCallbacks
def test_sso(mockConfig, apiServer, req, weirdo):
    """
    Does /api/sso create or return a good user?
    """
    pPost = patch.object(treq, 'post',
            return_value=defer.succeed(None),
            autospec=True)
    pGet = patch.object(treq, 'get',
            return_value=defer.succeed(None),
            autospec=True)

    @defer.inlineCallbacks
    def negotiateSSO(req=req, **user):
        def auth0tokenizer():
            return defer.succeed({'access_token': 'IDK!@#BBQ'})

        def auth0userGetter():
            return defer.succeed(dict(**user))

        pContent = patch.object(treq, 'json_content',
                side_effect=[auth0tokenizer(), auth0userGetter()],
                autospec=True)

        with pPost as mPost, pGet as mGet, pContent:
            yield apiServer.handler('sso', req)
            mPost.assert_called_once_with(
                server.TOKEN_URL,
                json.dumps({'client_id': 'abc123',
                 'client_secret': 'ABC!@#',
                 'redirect_uri': 'https://' + CONFIG.public_hostname + '/api/sso',
                 'code': 'idk123bbq',
                 'grant_type': 'authorization_code',
                 }, sort_keys=True),
                headers=ANY)
            mGet.assert_called_once_with(server.USER_URL + 'IDK!@#BBQ')

    # test once with an existing user
    reqJS = requestJSON([], args={'code': ['idk123bbq']})
    yield negotiateSSO(reqJS, email=weirdo.email)
    assert reqJS.getSession().user == weirdo
    assert reqJS.responseCode == 302
    assert reqJS.responseHeaders.getRawHeaders('location') == ['/']

    # test again with a new user
    reqJS = requestJSON([], args={'code': ['idk123bbq']})
    yield negotiateSSO(reqJS,
            email='weirdo2@gmail.com',
            family_name='2',
            given_name='weirdo'
            )
    assert reqJS.getSession().user.email == 'weirdo2@gmail.com'
    assert reqJS.responseCode == 302
    assert reqJS.responseHeaders.getRawHeaders('location') == ['/']


@inlineCallbacks
def test_noRecipeToBookmark(mockConfig, weirdo, apiServer):
    """
    Does the application still work if there are no recipes?
    """
    pageSource = ''
    pGet = patch.object(treq, 'get', return_value=defer.succeed(None), autospec=True)
    pTreqContent = patch.object(treq, 'content', return_value=defer.succeed(pageSource), autospec=True)

    with pGet, pTreqContent:
        reqJS = requestJSON([], session_user=weirdo)
        reqJS.args['uri'] = ['http://www.foodandwine.com/recipes/poutine-style-twice-baked-potatoes']
        ret = yield apiServer.handler('bookmarklet', reqJS)
        expectedResults = server.ClipResponse(
                status=RS.error, message=server.ResponseMsg.noRecipe,
                recipes=[],
                )
        assert ret == expectedResults


@inlineCallbacks
def test_bookmarklet(mockConfig, apiServer, specialUsers, weirdo, recipePageHTML):
    """
    Does api/bookmarklet fetch, save, and return a response for the recipe?
    """
    pGet = patch.object(treq, 'get', return_value=defer.succeed(None), autospec=True)
    pTreqContent = patch.object(treq, 'content', return_value=defer.succeed(recipePageHTML), autospec=True)

    with pGet, pTreqContent:
        # normal bookmarkleting
        reqJS = requestJSON([], session_user=weirdo)
        reqJS.args['uri'] = ['http://www.foodandwine.com/recipes/poutine-style-twice-baked-potatoes']
        ret = yield apiServer.handler('bookmarklet', reqJS)
        assert len(recipe.Recipe.objects()) == 1
        expectedResults = server.ClipResponse(
                status=RS.ok, message='',
                recipes=[{"name": "Delicious Meatless Meatballs", "urlKey": "weirdo-gmail-com-delicious-meatless-meatballs"}]
                )
        assert ret == expectedResults

        # not signed in to noms; bookmarkleting should not be allowed
        reqJS = requestJSON([])
        reqJS.args['uri'] = ['http://www.foodandwine.com/recipes/poutine-style-twice-baked-potatoes']
        ret = yield apiServer.handler('bookmarklet', reqJS)
        expectedResults = server.ClipResponse(
                status=RS.error, message=server.ResponseMsg.notLoggedIn,
                recipes=[],
                )
        assert ret == expectedResults


@fixture
def weirdSoupPOST():
    """
    Data structure for a recipe posted from the create form
    """
    return dict(
            name='Weird soup',
            author='Weird Soup Man',
            ingredients=['weirdness', 'soup'],
            instructions=['mix together ingredients', 'heat through'],
            )


@inlineCallbacks
def test_setHash(mockConfig, apiServer, localapi):
    """
    Do I update the static hash setting via the API?

    Am I able to access the API with token-based auth?
    - using requestJSON(...user=)

    """
    rq = requestJSON([], user=localapi)
    resp = yield apiServer.handler('setHash', rq, hash='orange-banana-peach')
    assert resp == OK(message="hash='orange-banana-peach'")


@inlineCallbacks
def test_createRecipeSave(mockConfig, apiServer, weirdo, weirdSoupPOST):
    """
    Do we save data from the create form successfully?
    """
    reqJS = requestJSON([], content=weirdSoupPOST, session_user=weirdo)
    resp = yield apiServer.handler('createRecipeSave', reqJS)
    assert resp == OK(message='weirdo-gmail-com-weird-soup-')

    # the second time we should get an error because it exists
    reqJS = requestJSON([], content=weirdSoupPOST, session_user=weirdo)
    resp = yield apiServer.handler('createRecipeSave', reqJS)
    assert resp == ERROR(message=server.ResponseMsg.renameRecipe)

    anonJS = requestJSON([])
    with raises(Forbidden):
        yield apiServer.handler('createRecipeSave', anonJS)
