import requests
import json
import time
import sys
import csv


def compute_host_query(URL):
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
    
    rows = []
    r0 = requests.get(url = URL, headers = headers, params = {'query': compute_host_metrics['host_cpu_utilization']})
    r0_json = r0.json()['data']['result']
    
    for result in r0_json:
        l = []
        l.append(result['metric'].get('instance', ''))
        rows.append(l)

    for metric_name, metric_value in compute_host_metrics.items():
        r1 = requests.get(url = URL, headers = headers, params = {'query': metric_value})
        r1_json = r1.json()['data']['result']
        row = 0
        for result in r1_json:
                l = []
                l.append(result['value'][1])
                rows[row].append(l[0])
                # rows.append(l[0])
                ts = []
                ts.append(time.time())
                rows[row].append(ts[0])
                row = row + 1     
    return rows


URL = "http://192.168.24.20:31179/prometheus/api/v1/query"
metrics_name = [ 'instance', 'host_cpu_utilization', 'host_cpu_rate_sum', 'host_load1_per_cpu', 'host_mem_utilization', 'host_netin_bytes_wo_lo',  'host_netin_bytes_total', 'host_netin_drop_wo_lo', 'host_netout_bytes_wo_lo',\
                     'host_netout_bytes_total', 'host_netout_drop_wo_lo', 'host_disk_io_time', 'host_disk_io_time_wght', 'timestamp']
data = compute_host_query(URL)
with open('compute_host_data', 'w') as f:
         write = csv.writer(f)
         write.writerow(metrics_name)

         for seq in range (0, 3):
            data = compute_host_query(URL)
            write.writerows(data)
            sys.stdout.flush()
            time.sleep(15)
         

