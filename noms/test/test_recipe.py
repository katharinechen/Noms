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


def test_saveOnlyOnce(mockDatabase): 
    """
    Test that we only save a recipe only once? 
    """
    u = user.User(email='hello@hello.com', roles=[user.Roles.user])
    u.save() 
    r = recipe.Recipe(name='Pasta', 
                      author='Katharine Chen', 
                      user=u, 
                      urlKey='something-unique', 
                      ingredients=['cookie', 'pasta'], 
                      instructions=['nom1', 'nom2', 'nom3'])

    r.saveOnlyOnce()
    assert len(recipe.Recipe.objects()) == 1 

    # call it again to test that save is not called again 
    r.saveOnlyOnce()  
    assert len(recipe.Recipe.objects()) == 1 
