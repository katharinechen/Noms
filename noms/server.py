"""
Twisted Web Routing 
"""
from twisted.web import static

from klein import Klein


class Server(object): 
  """
  The web server
  """
  app = Klein() 

  @app.route("/")
  def index(self, request): 
      return static.File("/Users/katharinechen/Noms/noms/templates/index.html")

  @app.route("/static/", branch=True)
  def static(self, request): 
      return static.File("./static")

resource = Server().app.resource