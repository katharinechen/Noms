from klein import Klein

class Server(object): 
  """
  The web server
  """
  app = Klein() 

resource = Server().app.resource