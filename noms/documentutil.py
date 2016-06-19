"""
Extend Document to make test cleanup easier
"""

from mongoengine import Document


# Monkey-patching this (which is done in tests) will make unsave() work
def onSave(doc):
    """
    This does nothing by default
    """


class ReverseableDocument(Document):
    """
    Base Document class that hooks into save so we can cleanup

    ReverseableDocument.collectObject() registers every object in an unsave
    list, but this does not get hooked up unless noms.test is imported
    """
    meta = {'abstract': True}

    def save(self):
        r = super(ReverseableDocument, self).save()
        onSave(self)
        return r
