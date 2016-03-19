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


