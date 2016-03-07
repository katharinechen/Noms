"""
Twisted Web Routing 
"""
from functools import wraps
import json

import mongoengine

from jinja2 import Environment, PackageLoader 

from twisted.web import static

from klein import Klein

from noms import urlify, DATABASE_NAME, eachMethod
from noms.recipe import Recipe 


class EmptyQuery(Exception): 
    """
    Returned empty query
    """

#Jinja template context
env = Environment(
        block_start_string='<%',
        block_end_string='%>',
        comment_start_string='<#',
        comment_end_string='#>',
        variable_start_string='<<',
        variable_end_string='>>', 
        loader=PackageLoader('noms', 'templates')
    )

def renderToAPI(function):
    """
    Converts raw objects into json string
    """  
    @wraps(function)
    # decorator takes g(x) and returns f(g(x))
    def innerFunction(*a, **kw): 

        ret = function(*a, **kw) 
        if not ret:
            raise EmptyQuery("Returned empty query")

        #array or one object 
        if isinstance(ret, mongoengine.Document): 
            ret = ret.toJSType() 
            return json.dumps(ret)
        elif isinstance(ret, (tuple, list, mongoengine.QuerySet)):
            obj = []
            for n in ret: 
                obj.append(n.toJSType()) 
            return json.dumps(obj)
        else: 
            assert False, "Unknown API return: %r" % ret  

    return innerFunction


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
        template = env.get_template("index.html")
        return template.render()

    @app.route("/recipes")
    def showRecipes(self, request):
        template = env.get_template("application.html")
        return template.render(partial="recipe-list.html") 

    @app.route("/recipes/new")
    def createRecipe(self, request): 
        template = env.get_template("application.html")
        return template.render(partial="new-recipe.html")

    @app.route("/recipes/<string:urlKey>")
    def showRecipe(self, request, urlKey): 
        """
        Show individual recipe pages 
        """
        # urlKey = unique id made up of email and recipe name 
        template = env.get_template("application.html")
        return template.render(partial="recipe.html")

    @app.route("/ingredients/new")
    def createIngredient(self, request): 
        template = env.get_template("application.html")
        return template.render(partial="new-ingredient.html")

    _api = None 
    @app.route("/api/", branch=True)
    def api(self, request):
        """
        Memoizating APIServer().app.resource() 
        """ 
        request.setHeader('content-type', 'application/json')
        request.setHeader('expires', "-1") 
        if self._api is None: 
            self._api = APIServer().app.resource() 
        return self._api


class APIServer(object): 
    """
    The web server for JSON API 
    """
    app = Klein() 

    @app.route("/recipe/list")
    @renderToAPI
    def data_recipeList(self, request):
        """
        List all recipes 
        """
        # we are only sending limited information to the client because of security risk 
        #recipeList = Recipe.objects().only('name', 'urlKey')
        recipeList = Recipe.objects()
        return recipeList

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
    @renderToAPI
    def data_getRecipe(self, request, urlKey): 
        """
        Return a specific recipe from its urlKey 
        """
        recipe = Recipe.objects(urlKey=urlKey).first()
        return recipe 

def main():
    """
    Return a resource to start our application
    """
    resource = Server().app.resource
    mongoengine.connect(db=DATABASE_NAME) 
    return resource() 