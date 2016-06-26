"""
Extend Document to make test cleanup easier
"""

from mongoengine import Document


def onSave(doc):
    """
    No-op override that happens during Document.save() for all documents.

    This is a hook that can be replaced in test code by monkey-patching
    documentutil.onSave() to do whatever setUp/tearDown you need to do.
    """


class NomsDocument(Document):
    """
    Base Document class that overrides save().

    Use this as the base class for all noms Documents, and then patch
    onSave() if you want to do anything special in a test.
    """
    meta = {'abstract': True}

    def save(self):
        """
        Save, and call onSave()
        """
        r = super(NomsDocument, self).save()
        onSave(self)
        return r
