"""
Twisted Web Routing
"""
import json
from functools import wraps

import attr

from codado import enum
from codado.kleinish.tree import enter

import microdata

from twisted.web import static
from twisted.internet import defer

import treq

from werkzeug.exceptions import Forbidden

from klein import Klein

from noms import urlify, secret, CONFIG
from noms.user import User, USER, Roles
from noms.recipe import Recipe
from noms import rendering 
from noms.interface import ICurrentUser
from noms.rendering import ResponseStatus as RS, OK, ERROR


TOKEN_URL = "https://{domain}/oauth/token".format(domain='nomsbook.auth0.com')
USER_URL = "https://{domain}/userinfo?access_token=".format(domain='nomsbook.auth0.com')
OAUTH_GRANT_TYPE = 'authorization_code'
RECIPE_SCHEMA = 'http://schema.org/Recipe'


ResponseMsg = enum(
        notLoggedIn='User was not logged in.', 
        noRecipe='There are no recipes on this page.', 
        renameRecipe='You already have a recipe with the same name. Rename?',
        )


def roles(allowed, forbidAction=Forbidden):
    """
    Request must belong to a user with the needed roles, or => 403
    """
    def wrapper(fn):
        @wraps(fn)
        def roleCheck(self, request, *a, **kw):
            u = ICurrentUser(request)
            for role in allowed:
                if role in u.roles:
                    return fn(self, request, *a, **kw)
            if forbidAction is Forbidden:
                raise Forbidden()
            else:
                return forbidAction()
        # XXX adding an attribute to allow external tools to document what's
        # going on in the API
        roleCheck._roles = allowed
        return roleCheck
    return wrapper


class Server(object):
    """
    The web server for html and miscell.
    """
    app = Klein()

    @app.route("/static/", branch=True)
    def static(self, request):
        # remove the hash
        if request.postpath and request.postpath[0].startswith('HASH-'):
            del request.postpath[0]
        else:
            print "WARNING: request under /static/ with no HASH- cache busting"
        return static.File("./static")

    @app.route("/")
    def index(self, request):
        return rendering.HumanReadable('index.html')

    @app.route("/recipes")
    def showRecipes(self, request):
        return rendering.HumanReadable('application.html',
                partial='recipe-list.html')

    @app.route("/recipes/new")
    def createRecipe(self, request):
        return rendering.HumanReadable('application.html',
                partial='recipe-new.html')

    @app.route("/recipes/<string:urlKey>")
    def showRecipe(self, request, urlKey):
        """
        Show individual recipe pages
        """
        # urlKey = unique id made up of author's email + recipe name
        return rendering.HumanReadable('application.html',
                partial='recipe.html',
                preload={'urlKey': urlKey}
                )

    @app.route("/ingredients/new")
    def createIngredient(self, request):
        return rendering.HumanReadable("application.html",
                partial="ingredient-new.html")

    @app.route("/api/", branch=True)
    @enter('noms.server.APIServer')
    def api(self, request, subKlein):
        """
        Endpoints under here are served as application/json with no caching allowed.

        We memoize APIServer().app.resource() so we only have to create one.
        """
        request.setHeader('content-type', 'application/json')
        request.setHeader('expires', "-1")
        request.setHeader("cache-control", "private, max-age=0, no-cache, no-store, must-revalidate")
        request.setHeader("pragma", "no-cache")
        return subKlein


def querySet(fn):
    """
    Unwraps queryset results
    """
    @wraps(fn)
    def deco(request, *a, **kw):
        r = fn(request, *a, **kw)
        return rendering.RenderableQuerySet(r).render(request)
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
        return Recipe.objects()

    @app.route("/recipe/create")
    @roles([Roles.user])
    def createRecipeSave(self, request):
        """
        Save recipes
        """
        data = json.load(request.content)
        data = {k.encode('utf-8'): v for (k,v) in data.items()}
        recipe = Recipe()
        recipe.name = data['name']
        recipe.user = ICurrentUser(request)
        recipe.urlKey = urlify(recipe.user.email, recipe.name)
        if Recipe.objects(urlKey=recipe.urlKey).first():
            return ERROR(message=ResponseMsg.renameRecipe)

        recipe.author = data.get('author', USER().anonymous.givenName)
        for i in data['ingredients']:
            recipe.ingredients.append(i)
        for i in data['instructions']:
            recipe.instructions.append(i)

        recipe.save()
        return OK()

    @app.route("/sethash/<string:hash>")
    @roles([Roles.localapi])
    def setHash(self, request, hash):
        CONFIG.staticHash = hash
        CONFIG.save()
        print 'New hash=%r' % CONFIG.staticHash
        return OK(message='hash=%r' % CONFIG.staticHash)

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

        NOTE: This request is always made by an auth0-hosted API client, not by the
        user's browser.
        """
        # Auth0 begins the handshake by giving us a code for the transaction
        code = request.args.get('code')[0]

        # Ask auth0 to continue, passing back the one-use code, and proving
        # that we are an authorized auth0 SP by using the client_secret.
        auth0ID, auth0Secret = secret.get('auth0')
        tokenPayload = {
          'client_id':     auth0ID,
          'client_secret': auth0Secret,
          'redirect_uri':  CONFIG.apparentURL + '/api/sso',
          'code':          code,
          'grant_type':    'authorization_code'
        }
        tokenInfo = yield treq.post(TOKEN_URL,
                json.dumps(tokenPayload, sort_keys=True),
                headers={'Content-Type': ['application/json']}
                ).addCallback(treq.json_content)

        # Ask auth0 to look up the right user in the IdP, by querying with access_token
        userURL = '{base}{access_token}'.format(base=USER_URL, **tokenInfo)
        userInfo = yield treq.get(userURL).addCallback(treq.json_content)

        # Get or create a user account matching auth0's reply
        u = User.objects(email=userInfo['email']).first()
        if u is None:
            u = User.fromSSO(userInfo)
            u.save()

        # Also associate that user with the session
        # TODO - persistent sessions
        request.getSession().user = u

        # Tell auth0 to redirect. This makes auth0 tell the browser to redirect.
        defer.returnValue(request.redirect('/'))

    @app.route("/user")
    def user(self, request):
        """
        The current user as data
        """
        return ICurrentUser(request)

    @staticmethod
    def clipError(**kw):
        defer.returnValue(ClipResponse(status=RS.error, **kw))

    @staticmethod
    def clipOK(**kw):
        defer.returnValue(ClipResponse(status=RS.ok, **kw))

    @app.route("/bookmarklet")
    @roles([Roles.user],
            forbidAction=lambda: APIServer.clipError(message=ResponseMsg.notLoggedIn))
    @defer.inlineCallbacks
    def bookmarklet(self, request):
        """
        Fetches the recipe for the url, saves the recipe, and returns a response to the chrome extension
        """
        u = ICurrentUser(request)

        url = request.args['uri'][0]
        pageSource = yield treq.get(url).addCallback(treq.content)
 
        items = microdata.get_items(pageSource)
        recipesSaved = []

        for i in items:
            itemTypeArray = [x.string for x in i.itemtype]
            if RECIPE_SCHEMA in itemTypeArray:
                recipe = i
                saveItem = Recipe.fromMicrodata(recipe, u.email)
                Recipe.saveOnlyOnce(saveItem)
                recipesSaved.append({"name": saveItem.name, "urlKey": saveItem.urlKey}) 
                break 
        
        if len(recipesSaved) == 0:
            self.clipError(message=ResponseMsg.noRecipe) 

        self.clipOK(recipes=recipesSaved)


@attr.s
class ClipResponse(rendering.ResponseData):
    """
    Response from using the chrome extension to clip
    """
    recipes = attr.ib(default=attr.Factory(list))

