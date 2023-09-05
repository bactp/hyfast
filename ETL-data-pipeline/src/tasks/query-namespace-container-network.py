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

def cluster_namespace_container_net_query(URL, cluster_name, namespace):
    """
    query metrics for each compute host by each host
    compute_host_cluster_URL: http://192.168.40.232:31270/api/v1/query
    """
    headers = {'X-Scope-OrgID': cluster_name}
    name =  namespace
    cluster_namespace_container_network_metrics = {
            'cluster_ns_container_network_receive_bytes_total': 'sum(rate(container_network_receive_bytes_total{namespace="' + name + '", name=~".+"}[5m])) by (name)',  
            'cluster_ns_container_network_receive_errors_total': 'sum(rate(container_network_receive_errors_total{namespace="' + name + '", name=~".+"}[5m])) by (name)', 
            'cluster_ns_container_network_receive_packets_dropped_total': 'sum(rate(container_network_receive_packets_dropped_total{namespace="' + name + '", name=~".+"}[5m])) by (name)', 
            'cluster_ns_container_network_receive_packets_total': 'sum(rate(container_network_receive_packets_total{namespace="' + name + '", name=~".+"}[5m])) by (name)', 
            'cluster_ns_container_network_transmit_bytes_total': 'sum(rate(container_network_transmit_bytes_total{namespace="' + name + '", name=~".+"}[5m])) by (name)', 
            'cluster_ns_container_network_transmit_errors_total': 'sum(rate(container_network_transmit_errors_total{namespace="' + name + '", name=~".+"}[5m])) by (name)', 
            'cluster_ns_container_network_transmit_packets_dropped_total': 'sum(rate(container_network_transmit_packets_dropped_total{namespace="' + name + '", name=~".+"}[5m])) by (name)', 
            'cluster_ns_container_network_transmit_packets_total': 'sum(rate(container_network_transmit_packets_total{namespace="' + name + '", name=~".+"}[5m])) by (name)' 
            }
    
    rows = []
    r0 = requests.get(url = URL, headers = headers, params = {'query': cluster_namespace_container_network_metrics['cluster_ns_container_network_receive_bytes_total']})
    r0_json = r0.json()['data']['result']
    for result in r0_json:
        l = []
        l.append(result['metric'].get('name', ''))
        rows.append(l)

    for metric_name, metric_value in cluster_namespace_container_network_metrics.items():
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
metrics_name = ['container', 'cluster_ns_container_network_receive_bytes_total', 'cluster_ns_container_network_receive_errors_total', 'cluster_ns_container_network_receive_packets_dropped_total', 'cluster_ns_container_network_receive_packets_total', 'cluster_ns_container_network_transmit_bytes_total', 'cluster_ns_container_network_transmit_errors_total', 'cluster_ns_container_network_transmit_packets_dropped_total' \
                , 'cluster_ns_container_network_transmit_packets_total', 'timestamp' ]


cluster_name = "central-cluster"
name_space = "kube-system"

file_name = cluster_name + name_space + '_container_network' + '_data.csv'

with open(file_name, 'w') as f:
         write = csv.writer(f)
         write.writerow(metrics_name)

         for seq in range (0, 2):
            data = cluster_namespace_container_net_query(URL, cluster_name, name_space)
            # print(data)
            write.writerows(data)
            sys.stdout.flush()
            time.sleep(15)
        
minioClient = warehouse_connection()

date = datetime.datetime.now()

path = "cluster-namespace-container-network/" + str(date.strftime("%Y")) + date.strftime("%m") + date.strftime("%d")
minioClient.fput_object(cluster_name, path, file_name, content_type='application/csv')
os.remove(file_name)


         

