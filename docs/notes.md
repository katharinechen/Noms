
# Notes


## Local tool configuration

- follow steps in devgettingstarted to `gcloud init` and `gcloud component install kubectl`


## Steps

- create noms project in google cloud

- create gke instance 1vCPU, 3.75GB, us-west1-b
    ```
    gcloud container clusters get-credentials cluster-1
    ```

- build a mongodb instance using [cloud launcher > mongodb](https://console.cloud.google.com/launcher/details/click-to-deploy-images/mongodb?q=mongo&project=noms-197618)
    - choices: instance type small (1.7GB mem), us-west1-b, 100gb extra disk
    - note the VM hostname shown [here](https://console.cloud.google.com/compute/instances?project=noms-197618)
        - e.g. `mongodb-0-servers-vm-0` - this address can be pinged from inside a pod
    - create a firewall rule in [the VPC firewall ingress list](https://console.cloud.google.com/networking/firewalls/list?project=noms-197618&tab=INGRESS) with configuration:
        - direction **ingress**, source ip range **10.20.0.0/14** (confirm this matches your gke container range), **Allow**, port **tcp:27017**

- create a configmap object
    ```
    kubectl create configmap nomsbook-com --from-env-file=deployment/configmap/env
    ```

    - ensure the right hostname for the mongodb instance is set by editing that file
