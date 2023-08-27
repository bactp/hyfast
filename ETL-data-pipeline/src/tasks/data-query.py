import requests
import json


# url = url = 'http://192.168.24.20:31179/prometheus/api/v1/query'
# metrics = 'container_cpu_cfs_throttled_seconds_total'
# headers = {'X-Scope-OrgID':'central-cluster'}

# response = requests.get(url, headers=headers, params={'query': metrics})

# print(response.json())
# metric_value = round(float(response.json()['data']['result'][0]['value'][1]),4)

# print(response.json())

def compute_host_query(query_url):
    """
    query metrics for each compute host by each host
    compute_host_cluster_URL: http://192.168.40.232:31270/api/v1/query
    """
    headers = {'X-Scope-OrgID':'compute-host'}
    compute_host_metrics = {
            'host_cpu_utilization': 'sum(instance:node_cpu_utilisation:rate5m) by (instance)',
            'host_cpu_rate_sum': 'sum(instance:node_cpu:rate:sum) by (instance)',
            'host_load1_per_cpu': 'sum(instance:node_load1_per_cpu:ratio) by (instance)',
            'host_mem_utilization': 'sum(instance:node_load1_per_cpu:ratio) by (instance)',
            'host_netin_bytes_wo_lo': 'sum(instance:node_network_receive_bytes_excluding_lo:rate5m) by (instance)',
            'host_netin_bytes_total': 'sum(instance:node_network_receive_bytes:rate:sum) by (instance)',
            'host_netin_drop_wo_lo': 'sum(instance:node_network_receive_drop_excluding_lo:rate5m) by (instance)',
            'host_netout_bytes_wo_lo': 'sum(instance:node_network_transmit_bytes_excluding_lo:rate5m) by (instance)',
            'host_netout_bytes_total': 'sum(instance:node_network_transmit_bytes:rate:sum) by (instance)',
            'host_netout_drop_wo_lo': 'sum(instance:node_network_transmit_drop_excluding_lo:rate5m) by (instance)',
            'host_disk_io_time': 'sum(instance_device:node_disk_io_time_seconds:rate5m) by (instance)',
            'host_disk_io_time_wght': 'sum(instance_device:node_disk_io_time_weighted_seconds:rate5m) by (instance)'}
    metrics = []
    for metric_name, metric_value in compute_host_metrics.items():
        try:
            response = requests.get(query_url, headers=headers, params={'query': metric_value})
            if bool(response.json()['data']['result']):
                test = round(float(response.json()['data']['result'][0]['value'][1]), 4)
                metrics.append(test)
            else:
                metrics.append(0)
        except:
            metrics.append(0)
        
        
    return metrics
