Getting Started
===============

This document will show you how to get up and running with ``Noms``.

Initial Setup
-------------
If this is your first time working with ``Noms``, you have to complete the following steps to get ``Noms`` running in your local environment. 

First, downalod ``Noms`` source files from ``Github``: :: 
	
	$ git clone git@github.com:corydodt/Noms.git

Build Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~
Setup a vritual environment, install ``virtualenwrapper``: ::

	$ pip install virtualenwrapper 

In your ``~/.bash-profile`` add: 

.. code-block:: bash
	
	source /usr/local/bin/virtualenvwrapper.sh

Continue by making your ``Noms`` your virtualenv: ::

	$ mkvirtualenv -a Noms noms

Go to ``~/.virtualenv/noms/postactivate`` and add the following lines:

.. code-block:: bash

	export PATH=$PATH:~/Noms/bin
	export PYTHONPATH=$PYTHONPATH:~/Noms

Next time, if you want to enter your virtual environment, you can simply use ``workon noms``. This will automatically drop you in your virtual environment. 

Install Requirements 
~~~~~~~~~~~~~~~~~~~~
Install all the necessary packages for ``Noms`` via ``pip``: ::

	$ pip install -U -r requirements.txt

For Macs, you need to install ``mongo`` by running following commands ::

	$ brew install mongodb
	$ ln -sfv /usr/local/opt/mongodb/*.plist ~/Library/LaunchAgents
	$ launchctl load ~/Library/LaunchAgents/homebrew.mxcl.mongodb.plist

We use ``sass`` for design. To install ``sass``::

	$ gem install bundler
	$ bundle install

.. note::  In addition, you will need to set up your secret-pair collection. You will need the file from someone that already has the project set up! 

Noms Extension
~~~~~~~~~~~~~~
As part of ``Noms``, there is a google chrome extension to clip recipes from websites and inser them into our application. To download this chrome extension: 

- Visit ``chrome://extensions/``. 
- Click on "developer mode". 
- You should see another button called "Load unpacked extension." Select that, and select the folder Noms/chrome. This should create a new chrome extension call ``Noms``. 
- You should be able to see it in your chrome extension bar!

Import Mock 
~~~~~~~~~~~
To import mock recipe data for testing :: 

	$ bin/noms-sample

Run Localhost 
~~~~~~~~~~~~~
To run to run the application on ``localhost``, you have to run ``workon Noms`` to enable the virtual environment. Once the virtual environment is enabled, you will see (noms) in front of the path. After this you can start the server by running the command ``noms`` in your terminal. Visit ``localhost:8080`` to see the current state of the application.

Ongoing Setup
-------------
Now that you have completed the initial setup, moving forward you will only need to do the following to set be ready to work on ``Noms``: 
	
- ``workon Noms`` will automatically drop you in your virtual environment. 
- ``bin/noms-samples`` will dump sample recipe data into your ``mongo`` database. 
- ``noms`` will start running the application locally. You can visit the website at ``localhost:8080``.  
