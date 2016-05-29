"""
Recipe Collection
"""
import datetime
import re 

from mongoengine import fields

from noms.rendering import RenderableDocument
from noms import urlify 


def clean(string): 
    res = re.sub('\s+', ' ', string)
    return res.strip()

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
    user = fields.StringField(require=True, default=u"katharinechen.ny@gmail.com")
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
    def fromMicrodata(cls, microdata): 
        """ 
        Create a recipe object from microdata
        """ 
        self = cls()
        self.name = clean(microdata.name) 
        self.author = clean(microdata.author.name) 
        self.urlKey = urlify(self.user, self.name) 
        for i in microdata.props['ingredients']: 
            self.ingredients.append(clean(i))

        array = microdata.props['recipeInstructions'][0].split('\n')
        for i in array: 
            i = clean(i)
            if i: 
                self.instructions.append(i)
        return self 

    def clip(saveItem): 
        """
        Save recipe from website
        """
        if Recipe.objects() and (recipe.urlKey == saveItem): 
            return
        saveItem.save() 
