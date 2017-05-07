"""
Tests of `whisk describe`
"""
import os
from inspect import cleandoc
import json

import attr

import git

from pytest import fixture, raises

from mock import patch, create_autospec, MagicMock

from noms.whisk import describe
from noms.whisk import tag


@fixture
def localEnvFile():
    """
    Create and then remove an environment file
    """
    f = open('local.env.pytest', 'w')
    f.write(cleandoc('''
        # this is a comment
        public_hostname=hello.world
        other_var="hello world"
        # this is a comment
        '''))
    f.close()
    ret = f.name
    yield f.name
    os.remove(ret)


def test_readEnvironmentFile(localEnvFile):
    """
    Do I parse a docker-style environment file similarly to docker?
    """
    exp = {'public_hostname': 'hello.world',
           'other_var': '"hello world"' # not a typo. docker includes the
                                        # quotes, so we must also include the
                                        # quotes!
           }
    assert describe.readEnvironmentFile(localEnvFile) == exp


def test_parseDescribe():
    """
    Do I parse the results of `git describe`? Do I detect errors?
    """
    s1error = 'asdf/asdf/asdf'
    s2 = 'asdf-10-g0g4v39x'
    s3 = 'asdf/asdf-10-g0g4v39x'
    with raises(ValueError):
        describe.parseDescribe(s1error)
    assert describe.parseDescribe(s2) == {'short': 'asdf-10-g0g4v39x',
            'name': 'asdf',
            'count': '10',
            'abbrev': '0g4v39x'}
    assert describe.parseDescribe(s3) == {'short': 'asdf-10-g0g4v39x',
            'name': 'asdf',
            'count': '10',
            'abbrev': '0g4v39x'}


@fixture
def nomsTag():
    """
    Produce a NomsTag with some sample data
    """
    nt = tag.NomsTag(
                created='2017-04-04T10:28:12.522496',
                message='we built this city',
                tag='asdf-10-g0g4v39x',
                certbot_flags='--staging',
                certbot_email='woohoo@looneytunes.com',
                )
    return json.dumps(attr.asdict(nt), indent=2, sort_keys=1)


@fixture
def readEnvironmentFileFake(localEnvFile):
    """
    Return a function that actually calls readEnvironmentFile but with a path
    that we control in place of local.env
    """
    _real = describe.readEnvironmentFile
    def inner(idc):
        assert idc == describe.LOCAL_ENV
        return _real(localEnvFile)

    return inner


@fixture
def gitRepo(request):
    """
    Return a git repo that returns a known value for `git describe`
    """
    obj = create_autospec(git.Repo)
    obj.return_value.git.describe = MagicMock(
            return_value=request.function.gitDescribeReturn
            )
    return obj


@fixture
def description():
    """
    A noms Description with some prefilled details
    """
    return describe.Description(
            NOMS_VERSION=('git describe', 'asdf-10-g0g4v39x'),
            NOMS_DB_HOST=('process environment', 'manga'),
            certbot_flags=('nomstag', '--staging'),
            certbot_email=('nomstag', 'woohoo@looneytunes.com'),
            public_hostname=('local.env', 'hello.world'),
            proxy_hostname=('cli', 'noms-main'),
            proxy_port=('cli', '9090'),
            )


def test_buildDescription(
        description,
        nomsTag,
        gitRepo,
        readEnvironmentFileFake):
    """
    Do I integrate the 5 sources of information correctly?
    """
    expected = description
    pEnv = patch.dict(os.environ, {
        'TRAVIS_COMMIT_MESSAGE': nomsTag,
        'NOMS_DB_HOST': 'manga',
        }, clear=True)
    pRepo = patch.object(describe, 'Repo', gitRepo)
    pReadEnv = patch.object(describe,
        'readEnvironmentFile',
        readEnvironmentFileFake)
    pExists = patch.object(os.path, 'exists', return_value=True)
    with pEnv, pRepo, pReadEnv, pExists:
        descr = describe.Description()
        actual = descr.build({'proxy_port': '9090'})

    assert actual == expected

test_buildDescription.gitDescribeReturn = 'asdf/asdf-10-g0g4v39x'


def test_buildDescriptionBadGit(gitRepo):
    """
    Do I bail out if `git describe` is unexpectedly malformatted?
    """
    pRepo = patch.object(describe, 'Repo', gitRepo)
    with raises(ValueError), pRepo:
        descr = describe.Description()
        descr.build()

test_buildDescriptionBadGit.gitDescribeReturn = 'bad/asdf/asdf-10-g0g4v39x'


def test_buildDescriptionBadNomsTag(
        description,
        gitRepo,
        readEnvironmentFileFake):
    """
    Do I ignore TRAVIS_COMMIT_MESSAGE if it's not a real nomstag?

    (i.e. nomstag:true is not part of the json)
    """
    description.certbot_flags = ('cli', '')
    description.certbot_email = ('cli', 'corydodt@gmail.com')
    description.NOMS_DB_HOST = ('cli', 'mongo')
    description.public_hostname = ('local.env', 'hello.world')
    description.proxy_port = ('cli', '8080')
    pRepo = patch.object(describe, 'Repo', gitRepo)
    pEnv = patch.dict(os.environ,
            {'TRAVIS_COMMIT_MESSAGE': '{"public_hostname": 1}'},
            clear=True)
    pReadEnv = patch.object(describe, 'readEnvironmentFile', readEnvironmentFileFake)
    with pRepo, pEnv, pReadEnv:
        descr = describe.Description()
        actual = descr.build()

    assert actual == description

test_buildDescriptionBadNomsTag.gitDescribeReturn = test_buildDescription.gitDescribeReturn

def test_postOptions(description,
        nomsTag,
        gitRepo,
        readEnvironmentFileFake,
        capsys):
    de = describe.Describe()
    pEnv = patch.dict(os.environ, {
        'TRAVIS_COMMIT_MESSAGE': nomsTag,
        'NOMS_DB_HOST': 'manga',
        }, clear=True)
    pRepo = patch.object(describe, 'Repo', gitRepo)
    pReadEnv = patch.object(describe,
        'readEnvironmentFile',
        readEnvironmentFileFake)
    pExists = patch.object(os.path, 'exists', return_value=True)
    with pEnv, pRepo, pReadEnv, pExists:
        de.postOptions()

    expectedOut = cleandoc('''
        # from cli
        proxy_hostname=noms-main
        proxy_port=9090

        # from git describe
        NOMS_VERSION=asdf-10-g0g4v39x

        # from local.env
        public_hostname=hello.world

        # from nomstag
        certbot_email=woohoo@looneytunes.com
        certbot_flags=--staging

        # from process environment
        NOMS_DB_HOST=manga
        ''').strip()
    out, err = capsys.readouterr()
    out = out.strip()
    assert out, err == (expectedOut, '')

test_postOptions.gitDescribeReturn = test_buildDescription.gitDescribeReturn
