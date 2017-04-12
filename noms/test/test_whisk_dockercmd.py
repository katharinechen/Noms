"""
Test the runtime of `whisk docker ..`
"""
import os
import re
from cStringIO import StringIO

from pytest import fixture

from codado.py import fromdir

from noms.whisk import dockercmd, describe


@fixture
def builddir(tmpdir):
    """
    Ensures removal of temp files after test run
    """
    s = str(tmpdir.mkdir('test_whisk_dockercmd'))
    print s
    return s

@fixture
def dockerobj(builddir):
    descr = describe.Describe().buildDescription()
    descr.NOMS_VERSION = ("idk", "asdfasdfasdf")

    dockr = dockercmd.Docker()
    dockr.description = descr
    dockr._deployment = fromdir(builddir)
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
