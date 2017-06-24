==========
Deployment
==========

This section discusses initial ops work and ongoing deployment tasks for the
Noms site.

Docker Architecture
-------------------
Our docker infrastructure has a total of 4 container images:

- ``noms-src`` volume container (which is everything in the noms git repo)
- ``noms-main`` container (which is all our runtime dependencies, e.g. python pip, dev, ruby packages. This will stay alive and run our code.)
- ``proximation`` container - a service that provides letsencrypt ssl support and reverse proxying for noms
- ``mongo`` (which we pull from DockerHub)

Enterprise Infrastructure
-------------------------

A number of one-time steps are required on
[ecs.nomsbook.com](http://ecs.nomsbook.com) to get it to run noms. This work
happens inside the instance environment, so it cannot be captured (easily) by
a docker image or a cloudformation script.

Run the ecs stack build
~~~~~~~~~~~~~~~~~~~~~~~

The first step that can't be handled by CloudFormation is the step to kick off
the CloudFormation build. This was run to generate the base hardware stack:

.. code-block:: bash

    whisk cloudform --build ecs

This step only needs to be performed once to create the noms enterprise
infrastructure.

Attach efs
~~~~~~~~~~

.. code-block:: bash

    EFS_FILESYSTEM_ID=fs-3816c491
    sudo mkdir /etc/letsencrypt
    sudo yum install -y vim nfs-utils
    cat << EOF | sudo tee -a /etc/fstab
    $EFS_FILESYSTEM_ID.efs.us-west-2.amazonaws.com:/letsencrypt /etc/letsencrypt nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,_netdev 0 0
    EOF
    mkdir efstmp
    sudo mount -t nfs4 \
        -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 \
        $EFS_FILESYSTEM_ID.efs.us-west-2.amazonaws.com:/ \
        efstmp
    sudo mkdir efstmp/letsencrypt/
    sudo umount efstmp
    rmdir efstmp
    sudo mount -a

This step only needs to be performed once to configure the noms infrastructure
to save SSL certificates permanently.


Launch proximation
~~~~~~~~~~~~~~~~~~

From a local checkout of noms,

.. code-block:: bash

    whisk cloudform --build proximation

This step only needs to be performed once to begin routing traffic to noms
instances.

Launch nomsite
~~~~~~~~~~~~~~

The easiest way to launch an instance of noms into this environment is to commit a tag. There are two possibilities.

1. Add a tag prefixed with ``devbuild-``. Any tag beginning with this string
   will become the new official `dev.nomsbook.com` site.

2. Add a tag prefixied with ``release-``. Any tag beginning with this string
   will become the new official `nomsbook.com` site.

This step can be performed many times, with either kind of tag. Every time a
new tag is pushed, it will result in a new version of noms on the
corresponding site.
