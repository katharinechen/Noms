"""
Twisted Web Routing 
"""
import mongoengine
from jinja2 import Environment, PackageLoader 

from twisted.web import static

from klein import Klein

from noms.recipe import Recipe 

DATABASE_NAME = "noms"

env = Environment(
        block_start_string='<%',
        block_end_string='%>',
        comment_start_string='<#',
        comment_end_string='#>',
        variable_start_string='<<',
        variable_end_string='>>', 
        loader=PackageLoader('noms', 'templates')
    )

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
    def recipes(self, request):
        template = env.get_template("application.html")
        return template.render() 

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
    def recipelist(self, request):
        recipeList = Recipe.objects().only('name')
        return recipeList.to_json()

def main():
    """
    Return a resource to start our application
    """
    resource = Server().app.resource
    mongoengine.connect(db=DATABASE_NAME) 
    return resource() 