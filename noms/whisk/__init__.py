"""
Subcommands of the noms command-line interface.

For help try

$ noms --help
"""
import inspect

from twisted.python import usage

from codado.tx import Main

from noms.whisk.describe import Describe
from noms.whisk.tag import Tag
from noms.whisk.sample import Sample
from noms.whisk.usertoken import UserToken
from noms.whisk.digester import Digester


def doc(cls):
    """
    Pull off the first line of documentation from a class
    """
    cdoc = inspect.cleandoc(cls.__doc__)
    return cdoc.split('\n')[0]


class BaseWhisk(Main):
    """
    A collection of tools for maintaining a noms instance
    """
    optParameters = [
            ['alias', None, 'noms', 'Alias for a database connection (see noms.DBAlias)'],
            ]
    subCommands = [
            ("describe", None, Describe, doc(Describe)),
            ("tag", None, Tag, doc(Tag)),
            ("sample", None, Sample, doc(Sample)),
            ("usertoken", None, UserToken, doc(UserToken)),
            ("digester", None, Digester, doc(Digester)),
            ]

    def postOptions(self):
        """
        Deal with missing subcommand
        """
        if self.subCommand is None:
            raise usage.UsageError("** Please specify a subcommand (see \"Commands\").")
