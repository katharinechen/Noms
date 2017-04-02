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


def doc(cls):
    """
    Pull off the first line of documentation from a class
    """
    cdoc = inspect.cleandoc(cls.__doc__)
    return cdoc.split('\n')[0]


class BaseOptions(Main):
    """
    A tap options object suitable for twistd to start, with noms-specific extras
    """
    synopsis = "whisk [subCommands]"
    subCommands = [
            ("describe", None, Describe, doc(Describe)),
            ("tag", None, Tag, doc(Tag)),
            ]

    def postOptions(self):
        """
        Deal with missing subcommand
        """
        if self.subCommand is None:
            self.synopsis = "whisk <subcommand>"
            raise usage.UsageError("** Please specify a subcommand (see \"Commands\").")
