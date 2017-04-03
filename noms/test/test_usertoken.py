"""
Test the tool that acquires usertokens from the command line
"""
import re

from noms.whisk import usertoken


TOKEN_RX = re.compile(r'[-a-zA-Z0-9+/_.]{120,}')


def test_get(weirdo, mockConfig):
    """
    When I call get, do I get a token?
    """
    weirdo.save()
    ret = usertoken.get(weirdo.email)
    # we can't predict much about the token besides that it'll be mostly
    # base64 charset, with some dots, and be about yay long. 
    assert TOKEN_RX.match(ret)


def test_options(weirdo, mockConfig, capsys):
    """
    Does the command-line parser fetch the right token
    """
    weirdo.save()
    o = usertoken.UserToken()
    o.parseArgs(weirdo.email)
    o.postOptions()
    out = capsys.readouterr()[0]
    assert TOKEN_RX.match(out)
