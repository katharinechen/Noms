"""
Tests of noms.server, mostly handlers
"""
from cStringIO import StringIO
import json

from twisted.trial import unittest
from twisted.web.test.requesthelper import DummyRequest
from twisted.python.components import registerAdapter
from twisted.internet import defer

from klein.app import KleinRequest, KleinResource
from klein.interfaces import IKleinRequest

from codado import eachMethod

from noms import server, fromNoms, config, recipe, urlify, user
from noms.rendering import EmptyQuery
from noms.test import mockConfig, wrapDatabaseAndCallbacks


# klein adapts Request to KleinRequest internally when the Klein() object
# begins handling a request. This isn't explicitly done for DummyRequest
# (because this is an object that only appears in tests), so we create our own
# adapter -- now we can use DummyRequest wherever a Klein() object appears in
# our code
registerAdapter(KleinRequest, DummyRequest, IKleinRequest)


class FnTest(unittest.TestCase):
    """
    Test top-level functions
    """
    @mockConfig()
    def test_querySet(self):
        """
        Does querySet(fn)() render the result of the cursor returned by fn?
        """
        def _configs(req):
            return config.Config.objects()

        configsFn = server.querySet(_configs)
        self.assertEqual(configsFn(None), '[{"apparentURL": "https://app.nomsbook.com"}]')


class BaseServerTest(unittest.TestCase):
    defaultHeaders = (
        ('user-agent', ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0)']),
        ('cookie', ['']),
        )

    serverCls = None

    def setUp(self):
        if hasattr(self, 'server'):
            "Using memoized server instance"
        else:
            self.__class__.server = self.serverCls()

        # feel free to replace this request with your own, but lots of tests
        # just need this.
        self.req = self.request([])
        self.reqJS = self.requestJSON([])

    def request(self, postpath, requestHeaders=defaultHeaders, responseHeaders=(), **kwargs):
        """
        Build a fake request for tests
        """
        req = DummyRequest(postpath)
        for hdr, val in requestHeaders:
            req.requestHeaders.setRawHeaders(hdr, val)

        for hdr, val in responseHeaders:
            req.setHeader(hdr, val)

        for k, v in kwargs.items():
            if k.startswith('session_'):
                ses = req.getSession()
                setattr(ses, k[8:], v)
            else:
                setattr(req, k, v)

        return req

    def requestJSON(self, postpath, requestHeaders=defaultHeaders, responseHeaders=(), **kwargs):
        """
        As ServerTest.request, but force content-type header, and coerce
        kwargs['content'] to the right thing
        """
        content = kwargs.pop('content', None)
        if isinstance(content, dict):
            kwargs['content'] = StringIO(json.dumps(content))
        elif content:
            kwargs['content'] = StringIO(str(content))
        else:
            kwargs['content'] = None

        responseHeaders = responseHeaders + (('content-type', ['application/json']),)
        req = self.request(postpath, requestHeaders, responseHeaders, **kwargs)

        return req

    def handler(self, handlerName, req=None, *a, **kw):
        """
        Convenience method, call a Server.app endpoint with a request
        """
        if req is None:
            # postpath is empty by default because we're directly executing the
            # endpoint, so there should be nothing left to consume in the url
            # path. In other words, we've already found the final resource when
            # execute_endpoint is called.
            postpath = kw.pop('postpath', [])
            req = self.request(postpath)

        return defer.maybeDeferred(
                self.server.app.execute_endpoint,
                handlerName, req, *a, **kw
                )


@eachMethod(wrapDatabaseAndCallbacks, 'test_')
class ServerTest(BaseServerTest):
    """
    Test server handlers
    """
    serverCls = server.Server

    def test_static(self):
        """
        Does /static/ return a FilePath?
        """
        with fromNoms:
            r = yield self.handler('static', postpath=['js', 'app.js'])
            self.assertTrue('app.js' in r.child('js').listdir())

    def test_index(self):
        """
        Does / return the home page?
        """
        r = yield self.handler('index', self.req)
        self.assertRegexpMatches(r.render(self.req), r'<title>NOM NOM NOM</title>')

    def test_showRecipes(self):
        """
        Does /recipes list recipes?
        """
        r = yield self.handler('showRecipes', self.req)
        self.assertRegexpMatches(r.render(self.req), r'partials/recipe-list.html')

    def test_createRecipe(self):
        """
        Does /recipes/new show the creation page?
        """
        r = yield self.handler('createRecipe', self.req)
        self.assertRegexpMatches(r.render(self.req), r'partials/recipe-new.html')

    def test_createIngredient(self):
        """
        Does /ingredients/new show the ingredient creation page?
        """
        r = yield self.handler('createIngredient', self.req)
        self.assertRegexpMatches(r.render(self.req), r'partials/ingredient-new.html')

    def test_showRecipe(self):
        """
        Does /recipes/xxx show recipe xxx?
        """
        r = yield self.handler('showRecipe', self.req, 'foo-gmail-com-honeyed-cream-cheese-pear-pie-')
        rendered = r.render(self.req)
        self.assertRegexpMatches(rendered, r'partials/recipe.html')
        self.assertRegexpMatches(rendered, r'nomsPreload.*urlKey.*foo-gmail-com-honeyed-cream-cheese-pear-pie-')

    def test_api(self):
        """
        Does the /api/ URL hand off to the right resource?
        """
        req = self.request([])

        def _cleanup():
            del self.server._api

        self.addCleanup(_cleanup)

        # does it create the _api object when needed?
        self.assertEqual(self.server._api, None)
        r1 = yield self.handler('api', req)
        self.assertIdentical(r1, self.server._api)
        self.assertTrue(isinstance(r1, KleinResource))

        # does it return the same _api object when requested again?
        r2 = yield self.handler('api', req)
        self.assertIdentical(r1, r2)


@eachMethod(wrapDatabaseAndCallbacks, 'test_')
class APIServerTest(BaseServerTest):
    """
    Test API handlers
    """
    serverCls = server.APIServer

    def _users(self):
        """
        Set up some users explicitly during a test
        """
        return (user.User(email='weirdo@gmail.com').save(),)

    def _recipes(self):
        """
        Set up some recipes explicitly during a test
        """
        author = u'cory'
        url = urlify(u'weird sandwich', author)
        r1 = recipe.Recipe(name=u'weird sandwich', author=author, urlKey=url).save()
        url = urlify(u'weird soup', author)
        r2 = recipe.Recipe(name=u'weird soup', author=author, urlKey=url).save()
        return (r1, r2)

    def test_getRecipe(self):
        """
        Does /recipe/.... return a specific recipe?
        """
        self._recipes()
        r = yield self.handler('getRecipe', self.reqJS, 'weird-soup-cory-')
        self.assertEqual(r['name'], 'weird soup')

    def test_recipeList(self):
        """
        Does /recipe/list return a structured list of recipes from the database?
        """
        yield self.assertFailure(self.handler('recipeList'), EmptyQuery)

        self._recipes()
        r = json.loads((yield self.handler('recipeList')))
        keys = [x['urlKey'] for x in r]
        self.assertEqual(keys, ['weird-sandwich-cory-', 'weird-soup-cory-'])

    def test_user(self):
        u = self._users()[0]
        req = self.requestJSON([], session_user=u)
        r = yield self.handler('user', req)
        self.assertEqual(r.email, 'weirdo@gmail.com')
