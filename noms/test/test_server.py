"""
Tests of noms.server, mostly handlers
"""
from cStringIO import StringIO
import json

from twisted.trial import unittest
from twisted.web.test.requesthelper import DummyRequest
from twisted.python.components import registerAdapter

from klein.app import KleinRequest, KleinResource
# from klein import KleinResource
from klein.interfaces import IKleinRequest

from codado import eachMethod

from noms import server, fromNoms, config
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


@eachMethod(wrapDatabaseAndCallbacks, 'test_')
class ServerTest(unittest.TestCase):
    """
    Test server handlers
    """
    defaultHeaders = (
        ('user-agent', ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0)']),
        ('cookie', ['']),
        )

    def setUp(self):
        if hasattr(self, 'server'):
            "Using memoized server instance"
        else:
            ServerTest.server = server.Server()

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
                setattr(req.session, k[8:], v)
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
        else:
            kwargs['content'] = StringIO(str(content))

        responseHeaders = responseHeaders + ('content-type', ['application/json'])
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

        return self.server.app.execute_endpoint(handlerName, req, *a, **kw)

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
        req = self.request([])
        r = yield self.handler('index', req)
        self.assertRegexpMatches(r.render(req), r'<title>NOM NOM NOM</title>')

    def test_showRecipes(self):
        """
        Does /recipes list recipes?
        """
        req = self.request([])
        r = yield self.handler('showRecipes', req)
        self.assertRegexpMatches(r.render(req), r'partials/recipe-list.html')

    def test_createRecipe(self):
        """
        Does /recipes/new show the creation page?
        """
        req = self.request([])
        r = yield self.handler('createRecipe', req)
        self.assertRegexpMatches(r.render(req), r'partials/recipe-new.html')

    def test_createIngredient(self):
        """
        Does /ingredients/new show the ingredient creation page?
        """
        req = self.request([])
        r = yield self.handler('createIngredient', req)
        self.assertRegexpMatches(r.render(req), r'partials/ingredient-new.html')

    def test_showRecipe(self):
        """
        Does /recipes/xxx show recipe xxx?
        """
        req = self.request([])
        r = yield self.handler('showRecipe', req, 'foo-gmail-com-honeyed-cream-cheese-pear-pie-')
        rendered = r.render(req)
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
