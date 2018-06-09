# Prepare a GKE cluster for Running Web-facing Workloads

You need to install some software and make some settings changes to use that software. These changes
prepare your cluster for a wide variety of workloads that have web-facing interfaces, using only
off-the-shelf open source software. We will not install any Noms-specific software in this walkthrough.

## Build GCE resources that we can use to run kubernetes

1. Create the noms project in google cloud (result: `noms-197618` is the id of our project)

2. Create a GKE instance. Make the following selections for your settings:
      - 1 vCPU
      - 3.75GB memory
      - region us-west1-b

    *N.b.* This step creates the cluster, which allows `gcloud container clusters` to do anything. Before we did this, there was no way to get those credentials. If 
    you're starting over, install the GCE SDK, do this step, **then** finish local setup with
    `gcloud container clusters get-credentials cluster-1`

3. Download the certificates that you need to run `kubectl` on our cluster.
    ```bash
    gcloud container clusters get-credentials cluster-1
    ```

## Install helm and cert-manager in our new cluster

1. Enable `corydodt@gmail.com` to act as a cluster admin and create roles,
then allow helm to do privileged cluster actions.

   `helm` requires credentials that GKE does not grant by default. These first steps 
   assign those credentials.

    ```bash
    kubectl create clusterrolebinding cluster-1-admin-binding \
        --clusterrole=cluster-admin \
        --user=corydodt@gmail.com

    kubectl create serviceaccount -n kube-system tiller

    kubectl create clusterrolebinding tiller-binding \
        --clusterrole=cluster-admin \
        --serviceaccount kube-system:tiller
    ```


2. Install helm's tiller component
    ```bash
    helm init --service-account tiller
    ```

3. Install cert-manager with helm
    
    Complete instructions: https://github.com/ahmetb/gke-letsencrypt/blob/master/README.md
    
    Use
    ```bash
    helm install \
        --name cert-manager \
        --namespace kube-system \
        stable/cert-manager \
        --set ingressShim.extraArgs='{--default-issuer-name=letsencrypt-prod,--default-issuer-kind=ClusterIssuer}'
    ```

## Launch a database in GCE
Our mongodb will live outside the cluster on a dedicated instance.

1. Build a mongodb instance using 
    [cloud launcher > mongodb](https://console.cloud.google.com/launcher/details/click-to-deploy-images/mongodb?q=mongo&project=noms-197618)

    Make the following selections for your settings:
      - instance type small (1.7GB mem)
      - region us-west1-b
      - add a 100gb extra disk

2. Make note of the VM hostname shown [here](https://console.cloud.google.com/compute/instances?project=noms-197618)
      - e.g. `mongodb-0-servers-vm-0`
      - this address can be pinged from inside a pod

    This host is not reachable from machines inside the cluster by default.
    Use a firewall rule to grant network access to the mongodb service from
    the cluster.

3. Create a firewall rule in [the VPC firewall ingress list](https://console.cloud.google.com/networking/firewalls/list?project=noms-197618&tab=INGRESS)

    Make the following selections for your settings:
      - direction **ingress**
      - source ip range **10.20.0.0/14** (confirm this matches your gke container range)
      - **Allow**
      - port **tcp:27017**
