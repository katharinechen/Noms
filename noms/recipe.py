"""
Recipe Collection
"""

import datetime 

from mongoengine import Document, fields

class Recipe(Document):   
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
    ingredients = fields.ListField(fields.StringField, require=True)
    instructions = fields.ListField(fields.StringField, require=True)
    recipeYield = fields.StringField()
    tags = fields.StringField()
    modified = fields.DateTimeField(default=datetime.datetime.now)

    meta = { 
      'indexes': ['name'] 
    }