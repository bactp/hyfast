import requests
import json
import time, datetime
import sys
import csv
import os
from minio import Minio

def warehouse_connection():
    client = Minio("192.168.24.20:30256",
                    access_key="XwMptXNrhYWMHj99",
                    secret_key="Uatsl7MkYaJVrABZAXRTXfQzbzJ9IwlW",
                    secure=False,
    )
    
    return client

def cluster_instance_query(URL, cluster_name):
    """
    query metrics for each compute host by each host
    compute_host_cluster_URL: http://192.168.40.232:31270/api/v1/query
    """
    headers = {'X-Scope-OrgID': cluster_name}
    cluster_instance_metrics = {
            'cluster_instance_cpu_utilization': 'sum(instance:node_cpu_utilisation:rate5m) by (instance)',
            'cluster_instance_cpu_rate_sum': 'sum(instance:node_cpu:rate:sum) by (instance)',
            'cluster_instance_load1_per_cpu': 'sum(instance:node_load1_per_cpu:ratio) by (instance)',
            'cluster_instance_mem_utilization': 'sum(instance:node_load1_per_cpu:ratio) by (instance)',
            'cluster_instance_netin_bytes_wo_lo': 'sum(instance:node_network_receive_bytes_excluding_lo:rate5m) by (instance)',
            'cluster_instance_netin_bytes_total': 'sum(instance:node_network_receive_bytes:rate:sum) by (instance)',
            'cluster_instance_netin_drop_wo_lo': 'sum(instance:node_network_receive_drop_excluding_lo:rate5m) by (instance)',
            'cluster_instance_netout_bytes_wo_lo': 'sum(instance:node_network_transmit_bytes_excluding_lo:rate5m) by (instance)',
            'cluster_instance_netout_bytes_total': 'sum(instance:node_network_transmit_bytes:rate:sum) by (instance)',
            'cluster_instance_netout_drop_wo_lo': 'sum(instance:node_network_transmit_drop_excluding_lo:rate5m) by (instance)',
            'cluster_instance_disk_io_time': 'sum(instance_device:node_disk_io_time_seconds:rate5m) by (instance)',
            'cluster_instance_disk_io_time_wght': 'sum(instance_device:node_disk_io_time_weighted_seconds:rate5m) by (instance)'}
    
    rows = []
    r0 = requests.get(url = URL, headers = headers, params = {'query': cluster_instance_metrics['cluster_instance_cpu_utilization']})
    r0_json = r0.json()['data']['result']
    
    for result in r0_json:
        l = []
        l.append(result['metric'].get('instance', ''))
        rows.append(l)

    for metric_name, metric_value in cluster_instance_metrics.items():
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
metrics_name = ['instance', 'cluster_instance_cpu_utilization', 'cluster_instance_cpu_rate_sum', 'cluster_instance_load1_per_cpu', 'cluster_instance_mem_utilization', 'cluster_instance_netin_bytes_wo_lo', 'cluster_instance_netin_bytes_total', 'cluster_instance_netin_drop_wo_lo' \
                , 'cluster_instance_netout_bytes_wo_lo', 'cluster_instance_netout_bytes_total', 'cluster_instance_netout_drop_wo_lo', 'cluster_instance_disk_io_time', 'cluster_instance_disk_io_time_wght', 'timestamp']


cluster_name = "central-cluster"

file_name = cluster_name + '_instance' + '_data.csv'

with open(file_name, 'w') as f:
         write = csv.writer(f)
         write.writerow(metrics_name)

         for seq in range (0, 2):
            data = cluster_instance_query(URL, cluster_name)
            # print(data)
            write.writerows(data)
            sys.stdout.flush()
            time.sleep(15)
        
minioClient = warehouse_connection()

date = datetime.datetime.now()

path = "cluster-instance/" + str(date.strftime("%Y")) + date.strftime("%m") + date.strftime("%d")
minioClient.fput_object(cluster_name, path, file_name, content_type='application/csv')
os.remove(file_name)


         

