import requests
import json
import time



# metrics = 'container_cpu_cfs_throttled_seconds_total'
# headers = {'X-Scope-OrgID':'central-cluster'}

# response = requests.get(url, headers=headers, params={'query': metrics})

# print(response.json())
# metric_value = round(float(response.json()['data']['result'][0]['value'][1]),4)

# print(response.json())

def compute_host_query(query_url, cluster_name):
    """
    query metrics for each compute host by each host
    compute_host_cluster_URL: http://192.168.40.232:31270/api/v1/query
    """
    headers = {'X-Scope-OrgID': cluster_name}
    cluster_metrics = {
        'cluster_MemUsage_Gib': 'sum(container_memory_working_set_bytes{id=~"/.*",instance=~"^.*$"})/1000000000',
        'cluster_CPUUsage_pct': 'sum(rate(container_cpu_usage_seconds_total{id=~"/.*",instance=~"^.*$"}[5m]))',
        'cluster_FSUsage_U': 'sum(rate(container_fs_usage_bytes{device=~"/dev/.*",id=~"/.*",instance=~"^.*$"}[5m]))',
        'cluster_NetIn_kBs': 'sum(rate(container_network_receive_bytes_total{instance=~"^.*$"}[5m]))/1000',
        'cluster_NetOut_kBs':  'sum(rate (container_network_transmit_bytes_total{instance=~"^.*$"}[5m]))/1000',
        'cluster_PodCPUUsage_pct': 'sum(rate (container_cpu_usage_seconds_total{image!="",name=~"^k8s_.*",kubernetes_io_hostname=~"^.*$"}[5m])) by (pod_name)',
        'cluster_PodMemUsage_Gib': 'sum(container_memory_working_set_bytes{image!="",name=~"^k8s_.*",kubernetes_io_hostname=~"^.*$"}) by (pod_name)/1000000000',
        'cluster_PodNetIn_kBs': 'sum(rate(container_network_receive_bytes_total{image!="",name=~"^k8s_.*",kubernetes_io_hostname=~"^.*$"}[5m])) by (pod_name) /1000',
        'cluster_PodNetOutt_kBs': 'sum(rate(container_network_transmit_bytes_total{image!="",name=~"^k8s_.*",kubernetes_io_hostname=~"^.*$"}[5m])) by (pod_name) /1000'
        }
    metrics = []
    for metric_name, metric_value in cluster_metrics.items():
        try:
            response = requests.get(query_url, headers=headers, params={'query': metric_value})
            response_json = response.json()['data']['result']
            print(response_json)
            if bool(response.json()['data']['result']):
                test = round(float(response.json()['data']['result'][0]['value'][1]), 4)
                metrics.append(test)
            else:
                metrics.append(0)
        except:
            print("none")
    ts = time.time()
    name = cluster_name
    metrics.append(ts)
    metrics.append(name)
    
    return metrics


url = 'http://192.168.24.20:31179/prometheus/api/v1/query'
cluster_name = "central-cluster"
metrics = compute_host_query(url, cluster_name)

print(metrics)