"""
Noms Python library - web application
"""
import re 

DATABASE_NAME = "noms"

def urlify(*args):
    """
    Return a url-friendly version of name
    """
    args = list(args)

    for n in args: 
        assert isinstance(n, unicode), "Arguments pass to urlify must be unicode"

    url = args.pop(0)
    for n in args: 
        url = url + "-" + n
    url = url.encode('punycode')

    return re.sub(r'[^-a-z0-9]', '-', url.lower()) 