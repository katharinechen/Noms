Docker
======

Docker Architecture
-------------------
Our docker infrastructure has a total of 4 container images: 

- ``noms-src`` volume container (which is everything in the noms git repo)
- ``noms-main`` container (which is all our runtime dependencies, e.g. python pip, dev, ruby packages. This will stay alive and run our code.)
- ``noms-nginx-front`` container (which just contains ``nginx``)
- ``mongo`` (which we pull from ``DockerHub``)

How to install docker?
----------------------
The best way to install docker by viewing the instructions provided on the official docker website. If this is your first time using docker with noms, you have to set up apt-cacher-ng. This service is required to build noms and greatly speeds up repeated builds of noms by caching the package downloads :: 

	$ docker pull sameersbn/apt-cacher-ng:latest

Make a directory by running ::

	$ sudo mkdir -p /srv/docker

Change permissions to your user :: 

	$ sudo chown $(id -u) /srv/docker
	$ docker run --name apt-cacher-ng -d --restart=always \
	    --publish 3142:3142 \
	    --volume /srv/docker/apt-cacher-ng:/var/cache/apt-cacher-ng \
	    sameersbn/apt-cacher-ng:latest

Download all docker images by running :: 

	$ noms-docker up 

This commands starts noms in a docker container after building the images if necessary.

Common Questions 
----------------
**Why does ``noms-nginx-front`` need its own container?**

``noms-nginx-front`` need its own container because we don't want to make our application SSL aware. We could have build this in noms-main but we want to separate the application from the SSL concerns by using nginx. Th nginx container to have two modes:
- ``get-cert-mode``: launch it with an environment variable that says which domain; in this mode, the container fetches a certificate for the domain from letsencrypt.
- ``run-mode``: launch it with an environment variable that says which domain; in this mode, the container starts up a web proxy. You cannot launch in run-mode unless the container was first initialized with get-cert-mod

**What is the difference between ``noms-docker up`` and ``noms-docker up --build``?**

If you want to rebuild the docker images, run ``noms-docker up --build``. Otherwise run ``noms-docker up``.
