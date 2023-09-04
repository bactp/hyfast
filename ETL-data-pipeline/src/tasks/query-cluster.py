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

def cluster_query(URL, cluster_name):
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
    
    rows = []
    for metric_name, metric_value in cluster_metrics.items():
        r1 = requests.get(URL, headers=headers, params={'query': metric_value})
        r1_json = r1.json()['data']['result']
        value = r1_json[0]['value'][1]
        rows.append(value)
    
    ts = str(time.time())
    name = str(cluster_name)
    rows.append(ts)
    rows.append(name)
    return rows


URL = "http://192.168.24.20:31179/prometheus/api/v1/query"
metrics_name = ['cluster_MemUsage_Gib', 'cluster_CPUUsage_pct', 'cluster_FSUsage_U', 'cluster_NetIn_kBs', 'cluster_NetOut_kBs',  'cluster_PodCPUUsage_pct', 'cluster_PodMemUsage_Gib', 'cluster_PodNetIn_kBs',\
                     'cluster_PodNetOutt_kBs', 'timestamp', 'cluster_name']

cluster_name = "central-cluster"

file_name = cluster_name + '_data.csv'
with open(file_name, 'w') as f:
         write = csv.writer(f)
         write.writerow(metrics_name)

         for seq in range (0, 2):
            rows =  []
            data = cluster_query(URL, cluster_name)
            rows.append(data)
            write.writerows(rows)
            sys.stdout.flush()
            time.sleep(10)
            
minioClient = warehouse_connection()

date = datetime.datetime.now()
path = "cluster/" + str(date.strftime("%Y")) + date.strftime("%m") + date.strftime("%d")
minioClient.fput_object('central-cluster', path, file_name, content_type='application/csv')
os.remove(file_name)