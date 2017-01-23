"""
Server configuration
"""
import re

from mongoengine import fields

from noms.rendering import RenderableDocument


class Config(RenderableDocument):
    """
    Config stored in the server
    """
    # URL used with in-pointing contexts, e.g. emailed links, 3rd-party
    # integrations, and anywhere we need to uniquely identify this instance
    apparentURL = fields.StringField(default='https://app.nomsbook.com',
            required=True, unique=True) # unique helps ensure we'll only have
                                        # one Config in the database

    cliOptions = fields.DictField() # options from NomsOptions, the cli parser class

    staticHash = fields.StringField()

    @property
    def appID(self):
        """
        => 'https-apps-nomsbook-com' for example

        A unique identifier for this instance of the app, for resources tied
        to the app that require a stable and globally-unique name, such as SQS
        queues or S3 buckets
        """
        return re.sub(r'[^a-zA-Z0-9]+', '-', self.apparentURL)

    def safe(self):
        """
        A representation of the config file suitable for use as a config file
        """
        return {'apparentURL': self.apparentURL}
