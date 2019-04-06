"""
Parsing Recipes from website with json-id
"""
import re
import microdata
import extruct
import requests
import urllib
from w3lib.html import get_base_url


RECIPE_SCHEMA = 'http://schema.org/Recipe'


def retrieveRecipes(url):
    """
    Retrieve recipes from url using various parsers
    """
    print("Sending the following URL to the first parser (microdata): {url}".format(url=url))
    recipes = parseWebData(url)

    if len(recipes) == 0:
        print("Sending the following URL to our second parser (extruct): {url}".format(url=url))
        recipes = parseWebData2(url)

    return recipes


def parseWebData(url):
    """
    Parse recipe website using microdata parser: https://github.com/edsu/microdata

    This seems to work for AllRecipes.com but not FoodandWine.com
    Example: https://www.allrecipes.com/recipe/246841/spicy-lime-avocado-soup/?internalSource=popular&referringContentType=Homepage
    """
    # there might be multiple objects with different schemas on a single webpage
    pageSource = urllib.urlopen(url)
    items = microdata.get_items(pageSource)
    recipes = [schemaParser1(r) for r in items if str(r.itemtype[0]) == RECIPE_SCHEMA]
    return recipes


def schemaParser1(data):
    """
    Process Recipe object using the format dictated RECIPE_SCHEMA
    """
    cleanInstructions = lambda x : re.sub('\s+', ' ', x).split(".")
    recipe = {}

    recipe['name'] = data.name
    recipe['author'] = data.author
    recipe['url'] = str(data.url)
    recipe['ingredients'] = data.get_all('recipeIngredient')
    recipe['instructions'] = cleanInstructions(data.recipeInstructions)
    recipe['recipeYield'] = data.recipeYield
    recipe['tags'] = data.get_all('keywords')

    return recipe


def parseWebData2(url):
    """
    Parse recipe website using extruct : https://github.com/scrapinghub/extruct

    This seems to work for FoodandWine.com but not AllRecipes
    Example: https://www.foodandwine.com/recipes/butter-beans-with-parsley-tomatoes-and-chorizo
    """
    r = requests.get(url)
    base_url = get_base_url(r.text, r.url)
    data = extruct.extract(r.text, base_url=base_url)
    recipes = [schemaParser2(r, url) for r in data['json-ld'] if r['@type'] == 'Recipe']  # Only recipes will be @type: 'Recipe'

    return recipes


def schemaParser2(data, url):
    """
    Process a Dict using the format dicated RECIPE_SCHEMA
    """
    recipe = {}

    recipe['name'] = data['name']
    recipe['author'] = data['author'][0]['name'] # only limiting to the first author
    recipe['url'] = url
    recipe['ingredients'] = data['recipeIngredient']
    recipe['instructions'] = data['recipeInstructions'].split('. ')
    recipe['recipeYield'] = data.get('recipeYield')
    recipe['tags'] = data.get('keywords')

    return recipe
