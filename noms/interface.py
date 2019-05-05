"""
Interfaces to use for building adapters
"""
from zope.interface import Interface


class ICurrentUser(Interface):
    """
    Fetch a user from a request
    """

