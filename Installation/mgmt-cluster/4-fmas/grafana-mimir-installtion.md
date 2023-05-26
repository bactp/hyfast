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

4. Edit values.yaml file for configuring mimir.
Example manifest.
[values.yaml](https://github.com/bactp/hyfast/tree/main/Installation/mgmt-cluster/4-fmas/values.yaml)

5. Install Grafana Mimir using the Helm chart:
```
helm install mimir grafana/mimir-distributed --values mimir-distributed/values.yaml -n mimir
```
Note: The output of the command contains the write and read URLs necessary for the following steps.
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
6. Check the statuses of the Mimir pods:

```
kubectl get po -n mimir
```
Wait until all of the pods have a status of Running or Completed, which might take a few minutes. The results lool similar to this:
```
grafana-6f47857589-zjjr2                    1/1     Running     0          36h
mimir-alertmanager-0                        1/1     Running     0          36h
mimir-compactor-0                           1/1     Running     0          36h
mimir-distributor-f8bf7959c-hvmqw           1/1     Running     0          36h
mimir-distributor-f8bf7959c-n7jwl           1/1     Running     0          36h
mimir-ingester-zone-a-0                     1/1     Running     0          36h
mimir-ingester-zone-b-0                     1/1     Running     0          36h
mimir-ingester-zone-c-0                     1/1     Running     0          36h
mimir-make-minio-buckets-5.0.7-7tfm2        0/1     Completed   0          36h
mimir-minio-cb7559f55-k4k9f                 1/1     Running     0          36h
mimir-nginx-b5c54f89d-bqqnt                 1/1     Running     0          36h
mimir-overrides-exporter-69f896db78-nn7tb   1/1     Running     0          36h
mimir-querier-7f9bb49b4-vg2c8               1/1     Running     0          36h
mimir-query-frontend-589dd56486-bn9v8       1/1     Running     0          36h
mimir-query-scheduler-db9648474-98kj5       1/1     Running     0          36h
mimir-query-scheduler-db9648474-bsvgh       1/1     Running     0          36h
mimir-rollout-operator-84d947659f-48pxw     1/1     Running     0          36h
mimir-ruler-7db5d9dd79-xdq7s                1/1     Running     0          36h
mimir-store-gateway-zone-a-0                1/1     Running     0          36h
mimir-store-gateway-zone-b-0                1/1     Running     0          36h
mimir-store-gateway-zone-c-0                1/1     Running     0          36h
```

## Start Grafana in Kubernetes and query metrics
1. Install grafana in the same Kubernetes cluster.
Pull grafana chart
```
helm pull grafana/grafana
```
edit service type to NodePort then Install grafana

```
helm install grafana grafana/grafana -n grafana
```
2. Get your 'admin' user password by running:
```
kubectl get secret --namespace mimir grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```
In a brower, go to the Grafana server at http://<IP>:<nginx-nodeport>,  Login and change admin password

3. On the left-hand side, go to Configuration > Data sources.
Configure a new Prometheus data source to query the local Grafana Mimir server, by using the following settings:
```
Name:   Mimir
URL:    http://192.168.24.20:32028/prometheus
```
4. Veritfy success:
You should be able to query metrics in Grafana Explore, as well as create dashboard panels by using your newly configured Mimir data source.

##  Configure Prometheus to write to Grafana Mimir
You can either configure Prometheus to write to Grafana Mimir or configure Grafana Agent to write to Mimir. Although you can configure both, you do not need to.

- Add the following YAML snippet to your Prometheus configuration file:
```
remote_write:
  - url: http://<ingress-host>/api/v1/push
```
In this case, your Prometheus server writes metrics to Grafana Mimir, based on what is defined in the existing scrape_configs configuration.

- Restart the Prometheus server.
