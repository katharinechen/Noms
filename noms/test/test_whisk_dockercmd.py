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
            {Name: 'mybaby'},
            {Name: 'notadir',
             Etc: !Ref notadir}
            ]}}}
            ''')

@fixture
def builddir(tmpdir, nomsiteYML):
    """
    Construct a directory full of files we need
    """
    builddir = str(tmpdir.mkdir('test_whisk_dockercmd'))
    _dir = fromdir(builddir)
    yml = open(_dir(dockercmd.NOMSITE_YML_IN), 'w')
    yml.write(nomsiteYML)
    yml.close()

    os.mkdir(_dir('hello'))
    open(_dir('hello', 'Dockerfile'), 'w')
    os.mkdir(_dir('mybaby'))
    open(_dir('mybaby', 'Dockerfile'), 'w')
    os.mkdir(_dir('notadir'))
    return builddir


@fixture
def dockerobj(builddir):
    """
    Docker() object configured to write to a tmp dir
    """
    descr = describe.Describe().buildDescription()
    descr.NOMS_VERSION = ("idk", "some_ver")

    dockr = dockercmd.Docker()
    dockr.client = dockerapi.from_env()
    dockr._deployment = fromdir(builddir)

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
    Do I stream the output of a successful build? Do I build the right dirs?

    Only dirs containing Dockerfiles get built.
    """
    assert dockerobj.images == {
            'hello': 'corydodt/hello:some_ver',
            'mybaby': 'corydodt/mybaby:some_ver',
            # this one will be ignored because no Dockerfile
            'notadir': 'corydodt/notadir:some_ver'
            }
    pBuild = patch.object(dockerobj.client.api, 'build',
            autospec=True,
            return_value=[{'stream': 'Hello'},
                {'stream': 'My baby'}
                ])
    with pBuild as mBuild:
        dockerobj.build()

    out, err = capsys.readouterr()
    assert re.search('-_- corydodt/hello:some_ver -_-', out)
    assert re.search('-_- corydodt/mybaby:some_ver -_-', out)
    assert err == ''

    calls = mBuild.call_args_list
    assert sorted(calls) == [
            call(cache_from=['corydodt/hello:some_ver'], decode=True,
                dockerfile=ANY, path='.', stream=True, tag='corydodt/hello:some_ver'),
            call(cache_from=['corydodt/mybaby:some_ver'], decode=True,
                dockerfile=ANY, path='.', stream=True, tag='corydodt/mybaby:some_ver'),
            ]


def test_buildError(dockerobj, capsys):
    """
    Do I fail as expected when the build has an error?
    """
    pBuild = patch.object(dockerobj.client.api, 'build',
            autospec=True,
            return_value=[{'stream': 'Hello'},
                {'error': 'My honey'}
                ])
    with pBuild as mBuild, raises(CLIError) as e:
        dockerobj.build()

    out, err = capsys.readouterr()
    assert re.match('^-_- corydodt.*\nHello\n', out)
    assert re.search(r'exit 1: My honey', str(e))

    # build only got called once due to the error
    mBuild.assert_called_once_with(
            cache_from=['corydodt/mybaby:some_ver'], decode=True,
            dockerfile=ANY, path='.', stream=True,
            tag='corydodt/mybaby:some_ver')


def test_push(dockerobj, capsys):
    """
    Do I make the api calls to push an image?
    """
    pPush = patch.object(dockerobj.client.api, 'push',
            autospec=True,
            return_value=[{'status': 'Hello'},
                {'progressDetail': 'My baby'},
                {'progressDetail': 'Hello'},
                {'status': 'My ragtime gaaal'}
                ])
    with pPush as mPush:
        dockerobj.push()

    out, err = capsys.readouterr()
    assert re.search('(\nHello\n\.\.My ragtime gaaal\n){2}', out)

    calls = mPush.call_args_list
    assert sorted(calls) == [
            call('corydodt/hello:some_ver', decode=True, stream=True, tag=None),
            call('corydodt/mybaby:some_ver', decode=True, stream=True, tag=None),
            ]


def test_pushError(dockerobj, capsys):
    """
    Do I error out at the correct time?
    """
    pPush = patch.object(dockerobj.client.api, 'push',
            autospec=True,
            return_value=[{'status': 'Hello'},
                {'progressDetail': 'My baby'},
                {'progressDetail': 'Hello'},
                {'error': 'My honey'},
                ])
    with pPush as mPush, raises(CLIError) as e:
        dockerobj.push()

    out, err = capsys.readouterr()
    assert re.search('Hello\n\.\.', out)
    assert re.search('exit 1: My honey', str(e))

    # push only got called once due to the error
    mPush.assert_called_once_with('corydodt/mybaby:some_ver', 
                decode=True, stream=True, tag=None)


def test_postOptionsError(builddir):
    """
    Do I make sure --build or --push is there?
    """
    dockerobj = dockercmd.Docker()
    dockerobj['build'] = dockerobj['push'] = False
    pFromdir = patch.object(dockercmd, 'fromdir',
            return_value=fromdir(builddir))
    with pFromdir, raises(CLIError) as e:
        dockerobj.postOptions()

    assert re.search('exit 1: --build or --push', str(e))


def test_postOptions(builddir):
    """
    Do I call the right things when the program runs?
    """
    dockerobj = dockercmd.Docker()
    dockerobj['build'] = dockerobj['push'] = True
    pBuildContext = patch.object(dockerobj, 'buildContext')
    pBuild = patch.object(dockerobj, 'build')
    pPush = patch.object(dockerobj, 'push')
    pFromdir = patch.object(dockercmd, 'fromdir',
            return_value=fromdir(builddir))

    with pPush as mPush, pBuild as mBuild, pBuildContext as mBuildContext, pFromdir:
        dockerobj.postOptions()

    mBuildContext.assert_called_once_with()
    mBuild.assert_called_once_with()
    mPush.assert_called_once_with()
