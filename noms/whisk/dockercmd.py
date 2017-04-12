"""
Manage build/push of docker images
"""
import os
import sys
import shutil

from twisted.python.procutils import which

import docker as dockerapi

import attr

import yaml

from jinja2 import Template

from codado.tx import Main, CLIError
from codado.py import fromdir

from noms.whisk import describe


DOCKER_ACCOUNT = 'corydodt'
NOMSITE_YML_IN = 'nomsite.yml.in'


def bangCtor(loader, tag_suffix, node):
    """
    Ignore !Ref, !Sub etc.
    """
    return node.value

yaml.add_multi_constructor('', bangCtor)


def jen(templateInput, envDescription):
    """
    Render a template through jinja to a string, using envDescription
    (an instance of noms.whisk.describe.Description)
    """
    tpl = Template(templateInput.read())
    env = {k: v[1] for (k, v) in attr.asdict(envDescription).items()}
    return tpl.render(__environ__=env)


class Docker(Main):
    """
    Build or push containers based on the nomsite ECS template
    """
    synopsis = "docker <--build|--push>"

    optFlags = [
            ['build', None, 'Build container images'],
            ['push', None, 'Push container images to docker.io'],
        ]

    def buildContext(self):
        """
        Create files in the build context that can't be built in a Dockerfile
        """
        buildd = fromdir(self._deployment('build'))
        if not os.path.exists(buildd()):
            os.mkdir(buildd())

        # use describe to write an env file
        open(buildd('env'), 'w'
                ).write(self.description.asEnvironment())
        print self.description.asEnvironment()

        # get jentemplate from PATH
        shutil.copyfile(which('jentemplate')[0], buildd('jentemplate'))

    def build(self):
        """
        Run the build for a directory containing a Dockerfile
        """
        for dirname in self.images:
            dest = self.images[dirname]
            print '-_-', dest, '-_' * 20
            df = self._deployment(dirname, 'Dockerfile')
            if not os.path.exists(df):
                continue

            stream = self.client.api.build(
                    path='.',
                    dockerfile=df,
                    tag=dest,
                    cache_from=[dest],
                    stream=True,
                    decode=True
                    )
            for line in stream:
                if 'stream' in line:
                    print line['stream'].strip()
                else:
                    raise CLIError(sys.argv[0], 1, line['error'])

    def push(self):
        """
        Upload all tagged images
        """
        for dirname in self.images:
            print
            df = self._deployment(dirname, 'Dockerfile')
            if not os.path.exists(df):
                continue

            stream = self.client.images.push(self.images[dirname],
                    stream=True, decode=True)
            for line in stream:
                if 'status' in line:
                    print line['status']
                elif 'progressDetail' in line:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                elif 'error' in line:
                    print line['error']

    def _getImageLabels(self):
        """
        Dict of image short names to full image labels to build
        """
        tplInput = open(self._deployment(NOMSITE_YML_IN))
        tpl = jen(tplInput, self.description)
        yml = yaml.load(tpl)
        containers = [x['Name'] for x in yml['Resources']['noms']['Properties']['ContainerDefinitions']]
        ver = self.description.NOMS_VERSION[1]
        fulls = ['%s/%s:%s' % (DOCKER_ACCOUNT, c, ver) for c in containers]
        ret = {short: full for (short, full) in zip(containers, fulls)}
        return ret

    def postOptions(self):
        self.client = dockerapi.from_env()
        self._deployment = fromdir('deployment')
        self.description = describe.Describe().buildDescription()
        self.images = self._getImageLabels()

        if not self['build'] and not self['push']:
            raise CLIError(sys.argv[0], 1, '--build or --push is required')

        if self['build']:
            self.buildContext()
            self.build()

        if self['push']:
            self.push()

