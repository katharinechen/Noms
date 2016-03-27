"""
Object publishing

- Render templates
- Conversions for various types into string
"""

import json

from jinja2 import Template, Environment, PackageLoader

from mongoengine import Document

from zope.interface import implements

from twisted.web import resource

from noms import CONFIG, secret


#Jinja template context
env = Environment(
        block_start_string='<%',
        block_end_string='%>',
        comment_start_string='<#',
        comment_end_string='#>',
        variable_start_string='<<',
        variable_end_string='>>',
        loader=PackageLoader('noms', 'templates')
    )

env.filters['json'] = json.dumps


class EmptyQuery(Exception):
    """
    Returned empty query
    """


class RenderableQuerySet(object):
    """
    A mongo queryset representable as a json array.

    The query must return RenderableDocuments
    """
    def __init__(self, querySet):
        self.qs = querySet

    def render(self, request):
        """
        Just wraps an array around the results
        """
        rr = list(self.qs)
        if not rr:
            raise EmptyQuery("Returned empty query")
        return json.dumps([o.safe() for o in rr]).encode('utf-8')


class HumanReadable(object):
    """
    Accepts a template and optional kwargs, returns an object that can be
    rendered to a string
    """
    implements(resource.IResource)
    isLeaf = True

    def __init__(self, templateOrFilename, **kwargs):
        if isinstance(templateOrFilename, Template):
            self.template = templateOrFilename
        elif isinstance(templateOrFilename, basestring):
            self.template = env.get_template(templateOrFilename)
        else:
            assert 0, "Got %r; needed a template or a template file" % templateOrFilename
        kwargs.setdefault('preload', {}).update({'apparentURL': CONFIG.apparentURL})
        kwargs['preload']['auth0Public'] = secret.get('auth0')[0]
        self.renderContext = kwargs

    def render(self, request):
        """
        Return a string version of this template
        """
        return self.template.render(**self.renderContext).encode('utf-8')


class RenderableDocument(Document):
    """
    A mongoengine Document that can be rendered as json

    Implement .safe() in a subclass which should return a json-dumpable value
    """
    implements(resource.IResource)
    meta = {'abstract': True}

    def render(self, request):
        return json.dumps(self.safe()).encode('utf-8')

    def safe(self):
        raise NotImplemented
