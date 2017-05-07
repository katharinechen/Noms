Getting Started
===============

This document will show you how to get up and running with ``Noms``.

Initial Setup
-------------
If this is your first time working with ``Noms``, here are the steps for you to get ``Noms`` running in your local environment. 

First, downalod Noms source files from ``Github`` :: 
	
	$ git clone git@github.com:corydodt/Noms.git

Setup a vritual environment, install ``virtualenwrapper`` ::

	$ pip install virtualenwrapper 

Add the following to your ``~/.bash-profile``

.. code-block:: bash
	
	source /usr/local/bin/virtualenvwrapper.sh

Continue by building creating your virtual ::

	$ mkvirtualenv -a Noms noms

Next time, if you want to enter your virtual environment, you can simply use ``workon noms``.

Install all packages that is necessary for ``Noms`` ::

	$ pip install -U -r requirements.txt

To make your executable files work, go to ``~/.virtualenv/noms/postactivate`` and add the following lines:

.. code-block:: bash

	export PATH=$PATH:~/Noms/bin
	export PYTHONPATH=$PYTHONPATH:~/Noms

For Macs, you need to install mongo and run the following commands ::

	$ brew install mongodb
	$ ln -sfv /usr/local/opt/mongodb/*.plist ~/Library/LaunchAgents
	$ launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mongodb.plist

To set up your database with the appropriate files: ``bin/noms-sample``. 

To install ``sass``::

	$ gem install bundler
	$ bundle install

Step up your secret pair collection. You will need the file from someone that already has the project set up! 

You only have to do these steps once!!!! 

Noms Extension
--------------
Visit ``chrome://extensions/``. Click on "developer mode". You should see another button called "Load unpacked extension." Select that, and select the folder Noms/chrome. This should create a new chrome extension call Noms. You should be able to see it in your extension bar!

Import Mock Recipes 
-------------------
To import mock recipe data :: 

	$ bin/noms-sample

Localhost 
---------
To run the application on localhost, you have to run ``workon Noms`` to enable the virtual environment. Once the virtual environment is enabled, you will see (noms) in front of the path. After this you can start the server by running the command ``noms`` in your terminal. Visit ``localhost:8080`` to see the current state of the application.

Testing 
-------
To run test on your local machine, use pytest. To see whether or not your test passes on the CI server, you can go to github and view travis. pytest is a tool to run tests. pytest also have a style of writing test. For Noms, we currently use pytest as a tool to run test, but use with pytest and pyUnit/trial style for writing tests. There are a few different ways to use pytest.

To run a specific test, use: pytest noms/test/test_rendering.py
To run all of the test, use: pytest
To run only the failing test, use pytest --lf 

Run Noms with Docker (Optional)
-------------------------------
You can run ``noms-docker`` up in your terminal.


