# Launch your first Noms workload into the cluster

Before launching into this walkthrough, make sure you have helm, cert-manager and a mongodb instance up and running. These steps are covered in `notes-prep-cluster`.

Now we will install some Noms data and create kubernetes resources for the Noms application.

## Install noms secrets as kubernetes secrets

While transitioning from database-backed secrets to cluster-backed secrets, we can use a tool to copy secrets from the database to the cluster.

1. Your database should have `localapi` and `auth0` in the `secret_pair` collection. You may have to manually insert these documents after getting the correct keys from Auth0.

1. Run the migration script:
    ```bash
    $ docs/experimental/savesecrets.py
    ```


## Create a certificate issuer for Noms to use

`cert-manager` (which you installed in the previous walkthrough) handles keeping the
TLS certificates up-to-date for Noms, but first we must tell it to start doing that.

This [tutorial](https://github.com/ahmetb/gke-letsencrypt) gives an outline of the process, which we have adapted here for Noms.

1. Create a global non-ephemeral IP address for your GCE project.
    ```bash
    gcloud compute addresses create noms-base-1-ip --global
    ```

1. Create `issuers` (a type of cert-manager resource) for Noms to use
    ```bash
    kubectl apply -f deployment/cluster-cert-manager-issuers.yml
    ```
    Resources built:
      1. issuer/letsencrypt-staging
      1. issuer/letsencrypt-prod


## Install the Noms application

1. Create the development namespace in the cluster, and put some roles in there that
   issuers can use to do the work.
    ```bash
    kubectl apply -f deployment/dev-nomsbook-com.yml
    ```
    Resources built:
      1. the namespace (you PROBABLY needed to create this early on, but having it here will not hurt)
      1. a serviceaccount for noms-base apps to bind permissions to
      1. a role/secrets-reader that grants some permissions to secrets
      1. rolebinding that associates sa/noms-base with role/secrets-reader

1. Create the noms pod and backend service
    ```bash
    kubectl apply -f deployment/noms-base-a.yml
    ```
    Resources built:
      1. the configmap built from the env file
      1. a deployment to start some pods **(This is the actual Noms application!)**
      1. svc/noms-base-1-backend make noms port 8080 available in the cluster


## Make Noms available on the Internet, with TLS

1. Create an ingress, to make it reachable from the Internet (no TLS yet)
    ```bash
    kubectl apply -f deployment/noms-base-b-ingress.yml
    ```
    Resources built:
      1. ingress/noms-base-1 with NO tls (we are staging it so letsencrypt can do an http challenge)

    This can take a few minutes; GCE is launching a load balancer.

1. Wait for the ingress to come online, check it with a web browser at http://dev.nomsbook.com until it's ready.

1. Ask `cert-manager` to create a certificate by using the http site to answer a challenge
    ```bash
    kubectl apply -f deployment/noms-base-c-cert.yml
    ```
    Resources built:
      1. secret/dev-nomsbook-com-tls

    This can also take a few minutes. There are several HTTP requests and responses between our cluster and Letsencrypt before it trusts us enough to issue a certificate.

1. Wait for the cert to be ready (check with `kubectl get secrets -n dev-nomsbook-com` and look for `dev-nomsbook-com-tls`)

1. Update the ingress to use the certificate:
    ```bash
    kubectl apply -f deployment/noms-base-d-tls.yml
    ```

    Resources *updated*:
      1. ingress/noms-base-1 *with* TLS

1. Wait a few more minutes for the ingress to shut down and come back up with TLS. Check https://dev.nomsbook.com until it's ready.
