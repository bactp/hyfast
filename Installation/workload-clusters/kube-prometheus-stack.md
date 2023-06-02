# Install helm if not exist.
```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh

```
# Get Helm Repository Info
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```
 then
 Pull kube-prometheus-stack charts to local
```
helm pull prometheus-community/kube-prometheus-stack --untar
```

Edit remote write url
```
- url: http://<ingress-host>/api/v1/push
```

Install prometheus-helm-chart

```
helm install prometheus prometheus-community/kube-prometheus-stack --values values.yaml
```

