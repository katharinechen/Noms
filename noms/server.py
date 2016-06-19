"""
Twisted Web Routing
"""
import json
from functools import wraps

from twisted.web import static
from twisted.internet import defer
import treq

from klein import Klein

from noms import urlify, user, secret, CONFIG
from noms.recipe import Recipe
from noms.rendering import HumanReadable, RenderableQuerySet


TOKEN_URL = "https://{domain}/oauth/token".format(domain='nomsbook.auth0.com')
USER_URL = "https://{domain}/userinfo?access_token=".format(domain='nomsbook.auth0.com')
OAUTH_GRANT_TYPE = 'authorization_code'


class Server(object):
    """
    The web server for html and miscell.
    """
    app = Klein()

    @app.route("/static/", branch=True)
    def static(self, request):
        return static.File("./static")

    @app.route("/")
    def index(self, request):
        return HumanReadable('index.html')

    @app.route("/recipes")
    def showRecipes(self, request):
        return HumanReadable('application.html',
                partial='recipe-list.html')

    @app.route("/recipes/new")
    def createRecipe(self, request):
        return HumanReadable('application.html',
                partial='recipe-new.html')

    @app.route("/recipes/<string:urlKey>")
    def showRecipe(self, request, urlKey):
        """
        Show individual recipe pages
        """
        # urlKey = unique id made up of author's email + recipe name
        return HumanReadable('application.html',
                partial='recipe.html',
                preload={'urlKey': urlKey}
                )

    @app.route("/ingredients/new")
    def createIngredient(self, request):
        return HumanReadable("application.html",
                partial="ingredient-new.html")

    _api = None
    @app.route("/api/", branch=True)
    def api(self, request):
        """
        Endpoints under here are served as application/json with no caching allowed.

        TODO: In the future, these will be REST APIs, so they can be requested
        using API keys instead of cookies.

        We memoize APIServer().app.resource() so we only have to create one.
        """
        request.setHeader('content-type', 'application/json')
        request.setHeader('expires', "-1")
        if self._api is None:
            self._api = APIServer().app.resource()
        return self._api


def querySet(fn):
    """
    Unwraps queryset results
    """
    @wraps(fn)
    def deco(request, *a, **kw):
        r = fn(request, *a, **kw)
        return RenderableQuerySet(r).render(request)
    return deco


class APIServer(object):
    """
    The web server for JSON API

    Organizes /api URLs
    """
    app = Klein()

    @app.route("/recipe/list")
    @querySet
    def recipeList(self, request):
        """
        List all recipes
        """
        # we are only sending limited information to the client because of security risk
        return Recipe.objects()

    @app.route("/recipe/create")
    def createRecipeSave(self, request):
        """
        Save recipes
        """
        data = json.load(request.content)
        data = { k.encode('utf-8'): v for (k,v) in data.items()}
        recipe = Recipe()
        recipe.name = data['name']
        recipe.author = data['author']
        recipe.urlKey = urlify(recipe.user, recipe.name)
        for i in data['ingredients']:
            recipe.ingredients.append(i)
        for i in data['instructions']:
            recipe.instructions.append(i)

        recipe.save()

    @app.route("/recipe/<string:urlKey>")
    def getRecipe(self, request, urlKey):
        """
        Return a specific recipe from its urlKey
        """
        return Recipe.objects(urlKey=urlKey).first()

    @app.route("/sso")
    @defer.inlineCallbacks
    def sso(self, request):
        """
        From the browser's access attempt via auth0, acquire the user from auth0
        """
        auth0ID, auth0Secret = secret.get('auth0')
        code = request.args.get('code')[0]

        tokenPayload = {
          'client_id':     auth0ID,
          'client_secret': auth0Secret,
          'redirect_uri':  CONFIG.apparentURL + '/api/sso',
          'code':          code,
          'grant_type':    'authorization_code'
        }
        r1 = yield treq.post(TOKEN_URL,
                json.dumps(tokenPayload),
                headers={'Content-Type': ['application/json']}
                ).addCallback(treq.content)
        tokenInfo = json.loads(r1)

        userURL = '{base}{access_token}'.format(base=USER_URL, **tokenInfo)
        r2 = yield treq.get(userURL).addCallback(treq.content)
        userInfo = json.loads(r2)
        u = user.User.objects(email=userInfo['email']).first()
        if u is None:
            u = user.User.fromSSO(userInfo)

        request.getSession().user = u

        defer.returnValue(request.redirect('/'))

    @app.route("/user")
    def user(self, request):
        """
        The current user as data
        """
        u = getattr(request.getSession(), 'user', user.ANONYMOUS)
        return u

