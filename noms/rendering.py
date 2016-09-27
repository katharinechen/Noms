"""
Object publishing

- Render templates
- Conversions for various types into string
"""

import json

from jinja2 import Template, Environment, PackageLoader

from zope.interface import implements

from twisted.web import resource

from noms import CONFIG, secret
from noms.documentutil import NomsDocument


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

env.filters['json'] = lambda x: json.dumps(x, cls=ResourceEncoder)


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
        return json.dumps([o.safe() for o in rr], cls=ResourceEncoder).encode('utf-8')


class ResourceEncoder(json.JSONEncoder): 
    """
    Replacement for default JSONEncoder that will render all RenderableDocuments as json 
    """
    def default(self, obj):
        if hasattr(obj, 'safe'): 
            return obj.safe()
        return json.JSONEncoder.default(self, obj)


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
        else: # pragma: no cover
            assert 0, "Got %r; needed a template or a template file" % templateOrFilename
        kwargs.setdefault('preload', {}).update({'apparentURL': CONFIG.apparentURL})
        kwargs['preload']['auth0Public'] = secret.get('auth0')[0]
        self.renderContext = kwargs

    def render(self, request):
        """
        Return a string version of this template
        """
        return self.template.render(**self.renderContext).encode('utf-8')


class RenderableDocument(NomsDocument):
    """
    A mongoengine Document that can be rendered as json

    Implement .safe() in a subclass which should return a json-dumpable value
    """
    implements(resource.IResource)
    meta = {'abstract': True}

    def render(self, request):
        """
        => JSON-encoded representation of this object's safe properties
        """
        return json.dumps(self.safe(), cls=ResourceEncoder).encode('utf-8')

    def safe(self):
        """
        => dict of document's fields, safe for presentation to the browser
        """
        raise NotImplementedError("implement safe in a subclass")
