"""
Recipe Collection
"""
import datetime
import re

from mongoengine import fields

from noms.rendering import RenderableDocument
from noms.user import User, USER
from noms import urlify


class Recipe(RenderableDocument):
    """
    Recipe Collection

    Things we eventually want to add:
    - calories
    - images for each steps
    - prep time
    - cook time
    - url or path
    - importedFrom
    """
    name = fields.StringField(require=True)
    author = fields.StringField(require=True) # author of the recipe
    user = fields.ReferenceField('User', dbref=False, require=True)
    urlKey = fields.StringField(require=True, unique=True) # combines user+name as the unique id
    ingredients = fields.ListField(fields.StringField(), require=True)
    instructions = fields.ListField(fields.StringField(), require=True)
    recipeYield = fields.StringField()
    tags = fields.ListField(fields.StringField())
    modified = fields.DateTimeField(default=datetime.datetime.now)

    meta = {
      'indexes': ['name'],
      'strict': False
    }

    def safe(self):
        """
        Filter out bad fields and return a dict
        """
        return {"name": self.name,
                "author": self.author,
                "user": self.user,
                "urlKey": self.urlKey,
                "ingredients": self.ingredients,
                "instructions": self.instructions,
                "recipeYield": self.recipeYield,
                "tags": self.tags,
                #"modified": self.modified (date is currently not going to work)
            }

    @classmethod
    def createFromWebclipper(cls, data, userEmail):
        """
        Create a recipe object from data from the web clipper
        """
        self = cls()
        self.name = data['name']
        self.author = data['author'] if  data['author'] else USER().anonymous.givenName
        self.user = User.objects.get(email=userEmail)
        self.urlKey = urlify(self.user.email, self.name)
        self.ingredients = data['ingredients']
        self.instructions = data['instructions']

        return self

    def saveOnlyOnce(self):
        """
        Save recipe from website
        """
        if Recipe.objects(urlKey=self.urlKey):
            return
        self.save()
