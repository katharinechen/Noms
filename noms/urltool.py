"""
URLtool - tool for documenting http API and building API clients
"""
from codado.tx import Main

from noms.server import Server, APIServer

import yaml


class Options(Main):
    synopsis = "urltool"
    ## optParameters = [[long, short, default, help], ...]

    def postOptions(self):
        ## """Recommended if there are subcommands:"""
        ## if self.subCommand is None:
        ##     self.synopsis = "{replace} <subcommand>"
        ##     raise usage.UsageError("** Please specify a subcommand (see \"Commands\").")
        services = [(Server, ''), (APIServer, '/api')]
        for service, prefix in services:
            rules = []
            for rule in service.app.url_map.iter_rules():
                rules.append(dumpRule(service, rule, prefix))
            print yaml.dump(sorted(rules))
            print '---'


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
