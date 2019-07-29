"""
Tests of `whisk sample`
"""
from noms import recipe, user
from noms.whisk import sample


def test_postOptions(mockConfig):
    """
    Do I invoke mongoimport on all these files
    """
    ss = sample.Sample()
    ss.postOptions()
    assert recipe.Recipe.objects.count() == 76
    assert user.User.objects.count() == 1
