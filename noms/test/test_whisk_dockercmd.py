"""
Test the runtime of `whisk docker ..`
"""
from inspect import cleandoc
import os
import re
from cStringIO import StringIO

import docker as dockerapi

from pytest import fixture, raises

from mock import patch, call, ANY

from codado.py import fromdir
from codado.tx import CLIError

from noms.whisk import dockercmd, describe


@fixture
def nomsiteYML():
    """
    YML string for testing the nomsite template parsing
    """
    return cleandoc('''
        Resources: {noms: {Properties: {ContainerDefinitions: [
            {Name: 'hello'},
            {Name: 'mybaby'}
            ]}}}
            ''')

@fixture
def dockerobj(tmpdir, nomsiteYML):
    """
    Docker() object configured to write to a tmp dir
    """
    builddir = str(tmpdir.mkdir('test_whisk_dockercmd'))
    descr = describe.Describe().buildDescription()
    descr.NOMS_VERSION = ("idk", "some_ver")

    dockr = dockercmd.Docker()
    dockr.client = dockerapi.from_env()
    dockr._deployment = fromdir(builddir)

    yml = open(dockr._deployment(dockercmd.NOMSITE_YML_IN), 'w')
    yml.write(nomsiteYML)
    yml.close()

    os.mkdir(dockr._deployment('hello'))
    open(dockr._deployment('hello', 'Dockerfile'), 'w')
    os.mkdir(dockr._deployment('mybaby'))
    open(dockr._deployment('mybaby', 'Dockerfile'), 'w')

    dockr.description = descr
    dockr.images = dockr._getImageLabels()
    return dockr


def test_jen():
    """
    Does the jen command generate a template?
    """
    descr = describe.Describe().buildDescription()
    descr.NOMS_VERSION = ("idk", "asdfasdfasdf")
    tpl = StringIO("!Ref {{ __environ__['NOMS_VERSION'] }} {{ __environ__['certbot_flags'] }}")
    assert dockercmd.jen(tpl, descr) == "!Ref asdfasdfasdf "


def test_buildContext(dockerobj):
    """
    Do I create the right files prior to building?
    """
    dockerobj.buildContext()
    env = open(dockerobj._deployment('build', 'env'))
    envData = env.read()
    assert re.search('NOMS_DB_HOST=mongo', envData)
    assert os.path.exists(dockerobj._deployment('build', 'jentemplate'))


def test_build(dockerobj, capsys):
    """
    Do I stream the output of a successful build?
    """
    assert dockerobj.images == {
            'hello': 'corydodt/hello:some_ver',
            'mybaby': 'corydodt/mybaby:some_ver'
            }
    pBuild = patch.object(dockerobj.client.api, 'build', 
            autospec=True,
            return_value=[{'stream': 'Hello'},
                {'stream': 'My baby'}
                ])
    with pBuild as mBuild:
        dockerobj.build()

    calls = mBuild.call_args_list
    assert sorted(calls) == [
            call(cache_from=['corydodt/hello:some_ver'], decode=True,
                dockerfile=ANY, path='.', stream=True, tag='corydodt/hello:some_ver'),
            call(cache_from=['corydodt/mybaby:some_ver'], decode=True,
                dockerfile=ANY, path='.', stream=True, tag='corydodt/mybaby:some_ver'),
            ]
    out, err = capsys.readouterr()
    assert re.search('-_- corydodt/hello:some_ver -_-', out)
    assert re.search('-_- corydodt/mybaby:some_ver -_-', out)
    assert err == ''


def test_buildError(dockerobj, capsys):
    """
    Do I fail as expected when the build has an error?
    """
    pBuild = patch.object(dockerobj.client.api, 'build', 
            autospec=True,
            return_value=[{'stream': 'Hello'},
                {'error': 'My honey'}
                ])
    with pBuild, raises(CLIError):
        dockerobj.build()

    out, err = capsys.readouterr()
    assert out == 'Hello\n'
    assert err == '** Blah bad: 1'
