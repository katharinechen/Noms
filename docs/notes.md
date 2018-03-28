
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

- create a secret object by running a script in noms:
    ```
    docs/experimental/savesecrets.py
    ```
    (You must have some secrets, such as the `auth0` secret, in your db already, for this to work)

- one-time only: enable corydodt@gmail.com to act as a cluster admin and create roles
    ```
    kubectl create clusterrolebinding cluster-1-admin-binding --clusterrole=cluster-admin --user=corydodt@gmail.com
    ```

- install helm's tiller component
    ```
    kubectl create serviceaccount -n kube-system tiller
    kubectl create clusterrolebinding tiller-binding --clusterrole=cluster-admin --serviceaccount kube-system:tiller
    helm init --service-account tiller
    ```

- install cert-manager with helm
    - https://github.com/ahmetb/gke-letsencrypt/blob/master/README.md
    - use
        ```
        helm install --name cert-manager --namespace kube-system stable/cert-manager --set ingressShim.extraArgs='{--default-issuer-name=letsencrypt-prod,--default-issuer-kind=ClusterIssuer}'
        ```

- Create noms resources using cert-manager to acquire TLS and associate it with an ingress
    - I followed this tutorial to get an idea https://github.com/ahmetb/gke-letsencrypt to learn how to do it
    - `gcloud compute addresses create noms-base-1-ip --global`
    - `kubectl apply -f deployment/cluster-cert-manager-issuers.yml` creates cluster-wide resources needed
      by `cert-manager` to talk to letsencrypt
        1. issuer/letsencrypt-staging
        1. issuer/letsencrypt-prod
    - `kubectl apply -f deployment/dev-nomsbook-com.yml` creates all 1-time k8s resources for the namespace:
        1. the namespace (you PROBABLY needed to create this early on, but having it here will not hurt)
        1. a serviceaccount for noms-base apps to bind permissions to
        1. a role/secrets-reader that grants some permissions to secrets
        1. rolebinding that associates sa/noms-base with role/secrets-reader
    - `kubectl apply -f deployment/noms-base-a.yml` creates required pod and backend service
        1. the configmap built from the env file
        1. a deployment to start some pods
        1. svc/noms-base-1-backend make noms port 8080 available in the cluster
    - `kubectl apply -f deployment/noms-base-b-ingress.yml` creates
        1. ingress/noms-base-1 with NO tls (we are staging it so letsencrypt can do an http challenge)
    - wait for the ingress to come online, check it with a web browser at http://dev.nomsbook.com. then,
        ```
        kubectl apply -f deployment/noms-base-c-cert.yml
        ```
        wait for the cert to be ready (check with `kubectl get secrets -n dev-nomsbook-com` and look for `dev-nomsbook-com-tls`)
    - Update the ingress with: `kubectl apply -f deployment/noms-base-d-tls.yml`
    - wait several minutes, then check https://dev.nomsbook.com
