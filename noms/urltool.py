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
            for rule in service.app.url_map.iter_rules():
                displayRule(service, rule, prefix)
            print '---'


def displayRule(serviceCls, rule, prefix):
    """
    Create a formatted display of the rule
    """
    data = {}
    endpoint = rule.endpoint
    branch = False
    if rule.endpoint.endswith('_branch'):
        endpoint = rule.endpoint[:-7]
        data['branch'] = True
    data['rule'] = prefix + rule.rule
    data['endpoint'] = '%s.%s' % (serviceCls.__name__, endpoint)
    meth = getattr(serviceCls, endpoint)

    if hasattr(meth, "_roles"):
        data['roles'] = meth._roles
    if hasattr(meth, '_json'):
        data['json'] = meth._json
    print yaml.dump(data, default_flow_style=False)
