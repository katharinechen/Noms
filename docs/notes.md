
# Notes

This file gives an outline of the process of setting up a Noms cluster from scratch. Most of these
steps only needed to be done one time, but this documentation serves as a record of how we did these
things in case we need to start over.


## Local tool configuration

You need to be able to run kubernetes commands with `kubectl` and GCE commands with `gcloud`, so
let's install the toolkits that give you those command-line utilities as well as the credentials
that allow you to interact with GCE from your local machine.

All Noms developers need to do this at least once, on any new machine where they intend to do
development work for Noms. 

- see `devgettingstarted` (section "Get Gcloud Credentials and Tools") for complete instructions


## Initial cluster preparation work

You need to install some software and make some settings changes to use that software. These changes
prepare your cluster for a wide variety of workloads that have web-facing interfaces.

- see `notes-prep-cluster.md`


### Build Noms-specific resources in the cluster

For Noms workloads in particular, install some Noms data and create kubernetes resources.
