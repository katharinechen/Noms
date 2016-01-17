"""
Twisted Web Routing 
"""
import mongoengine

from twisted.web import static

from klein import Klein

DATABASE_NAME = "noms"


class Server(object): 
  """
  The web server
  """
  app = Klein() 

  @app.route("/static/", branch=True)
  def static(self, request): 
      return static.File("./static")

  @app.route("/", branch=True)
  def index(self, request): 
    # https://github.com/twisted/klein/issues/41 
    f = static.File("./noms/templates/index.html")
    f.isLeaf = True 
    return f

def main():
  """
  Return a resource to start our application
  """
  resource = Server().app.resource

  mongoengine.connect(db=DATABASE_NAME) 

  return resource() 
