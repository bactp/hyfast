# Grafana Mimir using the Helm chart
The grafana mimir helm chart allows you to configure, install, and update grafana mimir within a kubernetes cluster

# Install Helm chart in a custom namespace
## Install helm if not exist.
```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```
## Install grafana-mimir
1. Create unique K8s ns for grafana mimir:

```
Kubectl create ns mimir
```
2. Set up a Helm repository using the following commands:

```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```
3. pull grafana/mimir-distributed for edit configuration
```
helm pull grafana/mimir-distributed --untar
```

4. Edit values.yaml file.


5. Install Grafana Mimir using the Helm chart:
```
helm install mimir grafana/mimir-distributed --values mimir-distributed/small.yaml -n mimir
```


6. 
```
Welcome to Grafana Mimir!
Remote write endpoints for Prometheus or Grafana Agent:
Ingress is not enabled, see the nginx.ingress values.
From inside the cluster:
  http://mimir-nginx.mimir.svc:30000/api/v1/push

Read address, Grafana data source (Prometheus) URL:
Ingress is not enabled, see the nginx.ingress values.
From inside the cluster:
  http://mimir-nginx.mimir.svc:30000/prometheus

```