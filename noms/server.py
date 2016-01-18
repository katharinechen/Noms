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
    The web server
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

    @app.route("/api/recipe/list")
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