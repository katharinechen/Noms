"""
Define database connections for code that needs mongo
"""

from mongoengine import connect


connect("noms-test")
