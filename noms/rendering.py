"""
Object publishing

- Render templates
- Conversions for various types into string
"""
from functools import partial
import json

from past.builtins import basestring
from builtins import object

import attr

from jinja2 import Template, Environment, PackageLoader

from zope.interface import implementer

from twisted.web import resource

from codado import enum

import noms
from noms import secret
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

env.filters['json'] = lambda x: json.dumps(x, cls=ResourceEncoder, sort_keys=True)


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
        return json.dumps([o.safe() for o in rr], cls=ResourceEncoder, sort_keys=True)


class ResourceEncoder(json.JSONEncoder): 
    """
    Replacement for default JSONEncoder that will render all RenderableDocuments as json 
    """
    def default(self, obj):
        if hasattr(obj, 'safe'): 
            return obj.safe()
        return json.JSONEncoder.default(self, obj)


@implementer(resource.IResource)
class HumanReadable(object):
    """
    Accepts a template and optional kwargs, returns an object that can be
    rendered to a string
    """
    isLeaf = True

    def __init__(self, templateOrFilename, **kwargs):
        if isinstance(templateOrFilename, Template):
            self.template = templateOrFilename
        elif isinstance(templateOrFilename, basestring):
            self.template = env.get_template(templateOrFilename)
        else: # pragma: no cover
            assert 0, "Got %r; needed a template or a template file" % templateOrFilename
        kwargs.setdefault('preload', {}).update(
                {'apparentURL': 'https://' + noms.CONFIG.public_hostname,
                 'staticHash': noms.CONFIG.staticHash,
                })
        kwargs['preload']['auth0Public'] = secret.get('auth0')[0]
        self.renderContext = kwargs

    def render(self, request):
        """
        Return a string version of this template
        """
        return self.template.render(**self.renderContext)


@implementer(resource.IResource)
class RenderableDocument(NomsDocument):
    """
    A mongoengine Document that can be rendered as json

    Implement .safe() in a subclass which should return a json-dumpable value
    """
    meta = {'abstract': True}

    def render(self, request):
        """
        => JSON-encoded representation of this object's safe properties
        """
        return json.dumps(self.safe(), cls=ResourceEncoder, sort_keys=True)

    def safe(self):
        """
        => dict of document's fields, safe for presentation to the browser
        """
        raise NotImplementedError("implement safe in a subclass")


ResponseStatus = enum(ok='ok', error='error')


@implementer(resource.IResource)
@attr.s
class ResponseData(object):
    """
    Generic container for an API response
    """

    status = attr.ib()
    message = attr.ib(default='')

    def render(self, request):
        """
        => JSON-encoded representation of this object's safe properties
        """
        return json.dumps(attr.asdict(self), cls=ResourceEncoder)


OK = partial(ResponseData, status=ResponseStatus.ok)
ERROR = partial(ResponseData, status=ResponseStatus.error)
