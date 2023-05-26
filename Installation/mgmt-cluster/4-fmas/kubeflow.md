# Reference
https://github.com/kubeflow/manifests

# Prepare manifests
Download Kubeflow version `v1.6.0`

```
https://github.com/kubeflow/manifests/archive/refs/tags/v1.6.0.tar.gz
```

Unzip and change folder name to `manifests`

# Installation
The example directory contains an example kustomization for the single command to be able to run.
In both options, we use a default email (user@example.com) and password (12341234). For any production Kubeflow deployment, you should change the default password by following the relevant section.

# Prerequisites
- Kubernetes (up to 1.25) with a default StorageClass
- kustomize 5.0.0
    warning Kubeflow is not compatible with earlier versions of Kustomize. This is because we need the sortOptions field, which is only available in Kustomize 5 and onwards #2388.
- kubectl

1. Single-cimmand installation

```
while ! kustomize build example | awk '!/well-defined/' | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
```
Once, everything is installed successfully, you can access the Kubeflow Central Dashboard by logging in to your cluster by access through `istio-ingressgateway` services.
```
kubectl get svc -n istio-system
```

```
NAME                    TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)                                                                      AGE
authservice             ClusterIP      10.108.91.221    <none>        8080/TCP                                                                     14h
cluster-local-gateway   ClusterIP      10.103.107.122   <none>        15020/TCP,80/TCP                                                             14h
istio-ingressgateway    LoadBalancer   10.111.214.127   <pending>     15021:32429/TCP,80:31884/TCP,443:30319/TCP,31400:31780/TCP,15443:30349/TCP   14h
istiod                  ClusterIP      10.101.215.55    <none>        15010/TCP,15012/TCP,443/TCP,15014/TCP                                        14h
knative-local-gateway   ClusterIP      10.98.176.220    <none>        80/TCP                                                                       14h
```

Use nodeIP:port (192.168.24.20:31884 as example) to access Kubeflow dashboard
Then, login with user@example.com/12341234 and you can see the Kubeflow dashboard.
2. Multi-command, Install individual components

#### cert-manager

cert-manager is used by many Kubeflow components to provide certificates for
admission webhooks.

Install cert-manager:

```sh
kustomize build common/cert-manager/cert-manager/base | kubectl apply -f -
kubectl wait --for=condition=ready pod -l 'app in (cert-manager,webhook)' --timeout=180s -n cert-manager
kustomize build common/cert-manager/kubeflow-issuer/base | kubectl apply -f -
```

In case you get this error:
```
Error from server (InternalError): error when creating "STDIN": Internal error occurred: failed calling webhook "webhook.cert-manager.io": failed to call webhook: Post "https://cert-manager-webhook.cert-manager.svc:443/mutate?timeout=10s": dial tcp 10.96.202.64:443: connect: connection refused
```
This is because the webhook is not yet ready to receive request. Wait a couple seconds and retry applying the manfiests.

For more troubleshooting info also check out https://cert-manager.io/docs/troubleshooting/webhook/

#### Istio

Istio is used by many Kubeflow components to secure their traffic, enforce
network authorization and implement routing policies.

Install Istio:

```sh
kustomize build common/istio-1-16/istio-crds/base | kubectl apply -f -
kustomize build common/istio-1-16/istio-namespace/base | kubectl apply -f -
kustomize build common/istio-1-16/istio-install/base | kubectl apply -f -
```

#### Dex

Dex is an OpenID Connect Identity (OIDC) with multiple authentication backends. In this default installation, it includes a static user with email `user@example.com`. By default, the user's password is `12341234`. For any production Kubeflow deployment, you should change the default password by following [the relevant section](#change-default-user-password).

Install Dex:

```sh
kustomize build common/dex/overlays/istio | kubectl apply -f -
```

#### OIDC AuthService

The OIDC AuthService extends your Istio Ingress-Gateway capabilities, to be able to function as an OIDC client:

```sh
kustomize build common/oidc-authservice/base | kubectl apply -f -
```

#### Knative

Knative is used by the KServe official Kubeflow component.

Install Knative Serving:

```sh
kustomize build common/knative/knative-serving/overlays/gateways | kubectl apply -f -
kustomize build common/istio-1-16/cluster-local-gateway/base | kubectl apply -f -
```

Optionally, you can install Knative Eventing which can be used for inference request logging:

```sh
kustomize build common/knative/knative-eventing/base | kubectl apply -f -
```

#### Kubeflow Namespace

Create the namespace where the Kubeflow components will live in. This namespace
is named `kubeflow`.

Install kubeflow namespace:

```sh
kustomize build common/kubeflow-namespace/base | kubectl apply -f -
```

#### Kubeflow Roles

Create the Kubeflow ClusterRoles, `kubeflow-view`, `kubeflow-edit` and
`kubeflow-admin`. Kubeflow components aggregate permissions to these
ClusterRoles.

Install kubeflow roles:

```sh
kustomize build common/kubeflow-roles/base | kubectl apply -f -
```

#### Kubeflow Istio Resources

Create the Istio resources needed by Kubeflow. This kustomization currently
creates an Istio Gateway named `kubeflow-gateway`, in namespace `kubeflow`.
If you want to install with your own Istio, then you need this kustomization as
well.

Install istio resources:

```sh
kustomize build common/istio-1-16/kubeflow-istio-resources/base | kubectl apply -f -
```

#### Kubeflow Pipelines

Install the [Multi-User Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/multi-user/) official Kubeflow component:

```sh
kustomize build apps/pipeline/upstream/env/cert-manager/platform-agnostic-multi-user | awk '!/well-defined/' | kubectl apply -f -
```
This installs argo with the safe-to use runasnonroot emissary executor.  Please note that the installer is still responsible to analyze the security issues that arise when containers are run with root access and to decide if the kubeflow pipeline main containers are run as runasnonroot. It is strongly recommended that the pipelines main containers are installed and run as runasnonroot and without any special capabilities to mitigate security risks.

Do not use the deprecated and insecure PNS executor anymore
```sh
kustomize build apps/pipeline/upstream/env/platform-agnostic-multi-user-pns | kubectl apply -f -
```

Refer to [argo workflow executor documentation](https://argoproj.github.io/argo-workflows/workflow-executors) for further reasoning.

**Multi-User Kubeflow Pipelines dependencies**

* Istio + Kubeflow Istio Resources
* Kubeflow Roles
* OIDC Auth Service (or cloud provider specific auth service)
* Profiles + KFAM

**Alternative: Kubeflow Pipelines Standalone**

You can install [Kubeflow Pipelines Standalone](https://www.kubeflow.org/docs/components/pipelines/installation/standalone-deployment/) which

* does not support multi user separation
* has no dependencies on the other services mentioned here

You can learn more about their differences in [Installation Options for Kubeflow Pipelines
](https://www.kubeflow.org/docs/components/pipelines/installation/overview/).

Besides installation instructions in Kubeflow Pipelines Standalone documentation, you need to apply two virtual services to expose [Kubeflow Pipelines UI](https://github.com/kubeflow/pipelines/blob/1.7.0/manifests/kustomize/base/installs/multi-user/virtual-service.yaml) and [Metadata API](https://github.com/kubeflow/pipelines/blob/1.7.0/manifests/kustomize/base/metadata/options/istio/virtual-service.yaml) in kubeflow-gateway.

#### KServe

KFServing was rebranded to KServe.

Install the KServe component:

```sh
kustomize build contrib/kserve/kserve | kubectl apply -f -
```

Install the Models web app:

```sh
kustomize build contrib/kserve/models-web-app/overlays/kubeflow | kubectl apply -f -
```

- ../contrib/kserve/models-web-app/overlays/kubeflow

#### Katib

Install the Katib official Kubeflow component:

```sh
kustomize build apps/katib/upstream/installs/katib-with-kubeflow | kubectl apply -f -
```

#### Central Dashboard

Install the Central Dashboard official Kubeflow component:

```sh
kustomize build apps/centraldashboard/upstream/overlays/kserve | kubectl apply -f -
```

#### Admission Webhook

Install the Admission Webhook for PodDefaults:

```sh
kustomize build apps/admission-webhook/upstream/overlays/cert-manager | kubectl apply -f -
```

#### Notebooks

Install the Notebook Controller official Kubeflow component:

```sh
kustomize build apps/jupyter/notebook-controller/upstream/overlays/kubeflow | kubectl apply -f -
```

Install the Jupyter Web App official Kubeflow component:

```sh
kustomize build apps/jupyter/jupyter-web-app/upstream/overlays/istio | kubectl apply -f -
```

#### Profiles + KFAM

Install the Profile Controller and the Kubeflow Access-Management (KFAM) official Kubeflow
components:

```sh
kustomize build apps/profiles/upstream/overlays/kubeflow | kubectl apply -f -
```

#### Volumes Web App

Install the Volumes Web App official Kubeflow component:

```sh
kustomize build apps/volumes-web-app/upstream/overlays/istio | kubectl apply -f -
```

#### Tensorboard

Install the Tensorboards Web App official Kubeflow component:

```sh
kustomize build apps/tensorboard/tensorboards-web-app/upstream/overlays/istio | kubectl apply -f -
```

Install the Tensorboard Controller official Kubeflow component:

```sh
kustomize build apps/tensorboard/tensorboard-controller/upstream/overlays/kubeflow | kubectl apply -f -
```

#### Training Operator

Install the Training Operator official Kubeflow component:

```sh
kustomize build apps/training-operator/upstream/overlays/kubeflow | kubectl apply -f -
```

#### User Namespace

Finally, create a new namespace for the the default user (named `kubeflow-user-example-com`).

```sh
kustomize build common/user-namespace/base | kubectl apply -f -
```

### Connect to your Kubeflow Cluster

After installation, it will take some time for all Pods to become ready. Make sure all Pods are ready before trying to connect, otherwise you might get unexpected errors. To check that all Kubeflow-related Pods are ready, use the following commands:

```sh
kubectl get pods -n cert-manager
kubectl get pods -n istio-system
kubectl get pods -n auth
kubectl get pods -n knative-eventing
kubectl get pods -n knative-serving
kubectl get pods -n kubeflow
kubectl get pods -n kubeflow-user-example-com
```

#### Port-Forward

The default way of accessing Kubeflow is via port-forward. This enables you to get started quickly without imposing any requirements on your environment. Run the following to port-forward Istio's Ingress-Gateway to local port `8080`:

```sh
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

After running the command, you can access the Kubeflow Central Dashboard by doing the following:

1. Open your browser and visit `http://localhost:8080`. You should get the Dex login screen.
2. Login with the default user's credential. The default email address is `user@example.com` and the default password is `12341234`.

#### NodePort / LoadBalancer / Ingress

In order to connect to Kubeflow using NodePort / LoadBalancer / Ingress, you need to setup HTTPS. The reason is that many of our web apps (e.g., Tensorboard Web App, Jupyter Web App, Katib UI) use [Secure Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#restrict_access_to_cookies), so accessing Kubeflow with HTTP over a non-localhost domain does not work.

Exposing your Kubeflow cluster with proper HTTPS is a process heavily dependent on your environment. For this reason, please take a look at the available [Kubeflow distributions](https://www.kubeflow.org/docs/started/installing-kubeflow/#install-a-packaged-kubeflow-distribution), which are targeted to specific environments, and select the one that fits your needs.

---
**NOTE**

If you absolutely need to expose Kubeflow over HTTP, you can disable the `Secure Cookies` feature by setting the `APP_SECURE_COOKIES` environment variable to `false` in every relevant web app. This is not recommended, as it poses security risks.

---

### Change default user password

For security reasons, we don't want to use the default password for the default Kubeflow user when installing in security-sensitive environments. Instead, you should define your own password before deploying. To define a password for the default user:

1. Pick a password for the default user, with email `user@example.com`, and hash it using `bcrypt`:

    ```sh
    python3 -c 'from passlib.hash import bcrypt; import getpass; print(bcrypt.using(rounds=12, ident="2y").hash(getpass.getpass()))'
    ```

2. Edit `common/dex/base/config-map.yaml` and fill the relevant field with the hash of the password you chose:

    ```yaml
    ...
      staticPasswords:
      - email: user@example.com
        hash: <enter the generated hash here>
    ```