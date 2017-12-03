.. _devgettingstarted:

==============================
Getting Started as a Developer
==============================

This document will show you how to get up and running with Noms.

Initial Setup
-------------

Get Source Code
~~~~~~~~~~~~~~~
If this is your first time working with Noms, you have to complete the
following steps to get Noms running in your local environment.

First, download Noms source files from Github: ::

    $ git clone git@github.com:corydodt/Noms.git

Set up a virtualenv
~~~~~~~~~~~~~~~~~~~

Install ``virtualenvwrapper``.

.. code-block:: bash

    $ sudo pip install virtualenvwrapper

In your ``~/.bash-profile`` add::

    source /usr/local/bin/virtualenvwrapper.sh

Build a virtual environment with ``virtualenvwrapper``.

.. code-block:: bash

    . /usr/local/bin/virtualenvwrapper.sh
    mkvirtualenv -a Noms noms
    cat <<'EOF' | tee -a ~/.virtualenvs/noms/bin/postactivate
    export PATH=$PATH:~/Noms/bin
    export PYTHONPATH=$PYTHONPATH:~/Noms
    EOF

When you wish to use this virtual environment, run ``workon noms``.

Get AWS Credentials
~~~~~~~~~~~~~~~~~~~

You will need a project maintainer to set up AWS account credentials for you.
When you have them, run ``aws configure`` and follow the prompts, as in the
example below.

If you already have working AWS credentials for the noms project, you do not
need to do this.

.. code-block:: bash

    $ aws configure
    AWS Access Key ID: AKIAUSEAREALAUTHKEYY
    AWS Secret Access Key: Use/your/actual/secret/key/here/pleaseee
    Default region name: us-west-2
    Default output format [text]:

Build Container Images
~~~~~~~~~~~~~~~~~~~~~~
It is easiest to run Noms inside of a preconfigured container. You can build
the container locally.

**As a prerequisite, you must have installed Docker already. If you are using
a Mac for development, you should install** `Docker for Mac`_.

.. _Docker for Mac: https://docs.docker.com/docker-for-mac/install/

.. code-block:: bash

    workon noms
    whisk docker --build
    # (commands run for a few minutes)
    # (to see what was built, run: docker images)

    # create a volume of your local source files
    docker volume create -o type=none -o device=$(pwd) -o o=bind noms-src
    # set some environment variables inside the container
    whisk describe > env
    cat <<EOF | tee -a env
    AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
    AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
    EOF

Run Localhost
~~~~~~~~~~~~~

First-time run
**************

You can run the Noms docker container with the following command::

   docker-compose -f deployment/docker-compose.yml up

Visit ``http://localhost:8080/`` to see the current state of the application.

The command above runs the containers in the foreground, allowing you to see
log output as it happens. OR, you can run it in the background, with::

    docker-compose -f deployment/docker-compose.yml up -d

After which, you can use ``docker logs -f deployment_noms-main_1`` to inspect
your container's output.

Editing source files
********************

You can edit the source files using any editor your choose, using the files in
the current directory. There is no need to use ``docker exec`` to run commands
inside the container, because all of your local source files are already
mounted in the container you started when you ran ``docker-compose``. This is
accomplished using the named volume ``noms-src`` that you created at the end
of `Build Container Images`.

Restarting
**********

You usually have two choices for restarting noms.

If you are running ``noms`` in the foreground (using the first command under
`First-time run`), you can simply press Ctrl+C, and run it again.

You can ALSO restart noms by running::

    docker kill -s HUP deployment_noms-main_1

Running Tests
~~~~~~~~~~~~~
Noms uses ``pytest`` as its backend test runner, and all tests are written in the ``pytest`` style.

To run test on your local machine, use ``pytest``. To see whether or not your
test passes on the CI server, you can go to ``github`` and view ``travis``.
``pytest`` is a tool to run tests, it also have a style of writing test.

There are a few different ways to use pytest:

- To run a specific test, use: ``pytest noms/test/test_rendering.py``
- To run all of the test, use: ``pytest``
- To run only the failing test, use: ``pytest --lf``

The foreground test runner is ``karma``. To run these tests, run::

.. code-block:: bash

    karma start

Noms Extension
~~~~~~~~~~~~~~
As part of Noms, there is a Google Chrome extension to clip recipes from
websites and save them into the application database. To download this chrome
extension:

- Visit ``chrome://extensions/``.
- Click on "developer mode".
- You should see another button called "Load unpacked extension." Select that,
  and select the folder Noms/chrome. This should create a new chrome extension
  called ``Noms``.
- You should be able to see it in your chrome extension bar!


Ongoing Steps
-------------
Now that you have completed the initial setup, moving forward you will only
need to do the following to set be ready to work on Noms:

- ``workon noms`` will automatically drop you into your virtual environment.
- ``docker-compose -f deployment/docker-compose.yml up`` will run the
  application in the foreground.
