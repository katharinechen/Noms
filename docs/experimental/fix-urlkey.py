# """
# Modify the recipe objects by adding an urlKey
# """

from mongoengine import connect

from noms import DATABASE_NAME, urlify 
from noms.recipe import Recipe


connect(db=DATABASE_NAME)  

recipes = Recipe.objects() 
for n in recipes: 
  n.urlKey = urlify(n.user, n.name) 
  n.save() 
