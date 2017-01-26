"""
URLtool - tool for documenting http API and building API clients
"""
import re

from codado.tx import Main

from noms.server import Server, APIServer

import yaml


class Options(Main):
    """
    Dump all urls in noms

    Apply optional <filter> as a regular expression searching within urls. For
    example, to match all urls beginning with api, you might use '^/api'
    """
    synopsis = "urltool [filter]"
    ## optParameters = [[long, short, default, help], ...]

    def parseArgs(self, filt=None):
        self['filt'] = re.compile(filt or '.*')

    def postOptions(self):
        ## """Recommended if there are subcommands:"""
        ## if self.subCommand is None:
        ##     self.synopsis = "{replace} <subcommand>"
        ##     raise usage.UsageError("** Please specify a subcommand (see \"Commands\").")
        services = [(Server, ''), (APIServer, '/api')]
        for service, prefix in services:
            rules = []
            for rule in service.app.url_map.iter_rules():
                rtop = dumpRule(service, rule, prefix)
                if self['filt'].search(rtop.keys()[0]):
                    rules.append(rtop)
            print yaml.dump(sorted(rules)) + '---'


def dumpRule(serviceCls, rule, prefix):
    """
    Create a dict representation of the rule
    """
    rtop = {prefix + rule.rule: {}}
    data = rtop.values()[0]
    endpoint = rule.endpoint
    if rule.endpoint.endswith('_branch'):
        endpoint = rule.endpoint[:-7]
        data['branch'] = True
    data['endpoint'] = '%s.%s' % (serviceCls.__name__, endpoint)
    meth = getattr(serviceCls, endpoint)

    if hasattr(meth, "_roles"):
        data['roles'] = meth._roles
    if hasattr(meth, '_json'):
        data['json'] = meth._json
    return rtop
