"""
Parsing Recipes from website with json-id
"""
import re
import microdata
import extruct
from w3lib.html import get_base_url

import treq
from twisted.internet import defer


RECIPE_SCHEMA = 'http://schema.org/Recipe'


@defer.inlineCallbacks
def retrieveRecipes(url):
    """
    Retrieve recipes from url using various parsers
    """
    print("Sending the following URL to the first parser (microdata): {url}".format(
        url=url))

    res = yield treq.get(url)
    rawData = yield res.content()
    recipes = parseWebData(rawData)

    if len(recipes) == 0:
        print("Sending the following URL to our second parser (extruct): {url}".format(
            url=url))
        recipes = parseWebData2(rawData, url)

    defer.returnValue(recipes)


def parseWebData(rawData):
    """
    Parse recipe website using microdata parser: https://github.com/edsu/microdata

    This seems to work for AllRecipes.com but not FoodandWine.com
    Example: https://www.allrecipes.com/recipe/246841/spicy-lime-avocado-soup/?internalSource=popular&referringContentType=Homepage
    """
    # there might be multiple objects with different schemas on a single webpage
    items = microdata.get_items(rawData)
    recipes = [schemaParser1(r) for r in items if str(
        r.itemtype[0]) == RECIPE_SCHEMA]
    return recipes


def schemaParser1(data):
    """
    Process Recipe object using the format dictated RECIPE_SCHEMA
    """
    def cleanInstructions(x): return re.sub('\s+', ' ', x).split(".")
    recipe = {}

    recipe['name'] = data.name
    recipe['author'] = data.author
    recipe['url'] = str(data.url)
    recipe['ingredients'] = data.get_all('recipeIngredient')
    recipe['instructions'] = cleanInstructions(data.recipeInstructions)
    recipe['recipeYield'] = data.recipeYield
    recipe['tags'] = data.get_all('keywords')

    return recipe


def parseWebData2(rawData, url):
    """
    Parse recipe website using extruct : https://github.com/scrapinghub/extruct

    This seems to work for FoodandWine.com but not AllRecipes
    Example: https://www.foodandwine.com/recipes/butter-beans-with-parsley-tomatoes-and-chorizo
    """
    base_url = get_base_url(rawData, url)
    data = extruct.extract(rawData, base_url=base_url)
    # Only recipes will be @type: 'Recipe'
    recipes = [schemaParser2(x, url)
               for x in data['json-ld'] if x['@type'] == 'Recipe']
    return recipes


def schemaParser2(data, url):
    """
    Process a Dict using the format dicated RECIPE_SCHEMA
    """
    recipe = {}

    recipe['name'] = data['name']
    # only limiting to the first author
    recipe['author'] = data['author'][0]['name']
    recipe['url'] = url
    recipe['ingredients'] = data['recipeIngredient']
    recipe['instructions'] = data['recipeInstructions'].split('. ')
    recipe['recipeYield'] = data.get('recipeYield')
    recipe['tags'] = data.get('keywords')

    return recipe
