"""
Twisted Web Routing 
"""
import mongoengine

from twisted.web import static

from klein import Klein

from noms.recipe import Recipe 

DATABASE_NAME = "noms"


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
        # https://github.com/twisted/klein/issues/41 
        f = static.File("./noms/templates/index.html")
        f.isLeaf = True 
        return f

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