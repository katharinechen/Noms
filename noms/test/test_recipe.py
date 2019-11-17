"""
Test the Recipe object
"""
from noms import recipe, user


def test_safe():
    """
    Do I produce a web-safe rendering of the user object?
    """
    u = user.User(email='hello@hello.com', roles=[user.Roles.user])
    r = recipe.Recipe(name='Pasta',
                      author='Katharine Chen',
                      user=u,
                      urlKey='something-unique',
                      ingredients=['cookie', 'pasta'],
                      instructions=['nom1', 'nom2', 'nom3'])
    expected = {"name": 'Pasta',
                "author": 'Katharine Chen',
                "user": u,
                "urlKey": 'something-unique',
                "ingredients": ['cookie', 'pasta'],
                "instructions": ['nom1', 'nom2', 'nom3'],
                "recipeYield": None,
                "tags": []}
    assert r.safe() == expected


def test_saveOnlyOnce(mockDatabase, weirdo):
    """
    Test that we only save a recipe only once?
    """
    r = recipe.Recipe(name='Pasta',
                      author='Katharine Chen',
                      user=weirdo,
                      urlKey='something-unique',
                      ingredients=['cookie', 'pasta'],
                      instructions=['nom1', 'nom2', 'nom3'])

    r.saveOnlyOnce()
    assert len(recipe.Recipe.objects()) == 1

    # call it again to test that save is not called again
    r.saveOnlyOnce()
    assert len(recipe.Recipe.objects()) == 1


def test_createFromWebclipper(mockDatabase, weirdo, recipeData):
    """
    Does fromMicrodata create a good Recipe?
    """
    ret = recipe.Recipe.createFromWebclipper(recipeData, u'weirdo@gmail.com')
    assert ret.author == u"Cory Dodt"
    assert ret.name == u'Delicious Meatless Meatballs'
    assert ret.urlKey == u'weirdo-gmail-com-delicious-meatless-meatballs-'

    # again, but blank the author
    del recipeData["author"]
    ret = recipe.Recipe.createFromWebclipper(recipeData, u'weirdo@gmail.com')
    assert ret.author == user.USER().anonymous.givenName
