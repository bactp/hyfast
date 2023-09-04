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

def cluster_namespace_container_query(URL, cluster_name, namespace):
    """
    query metrics for each compute host by each host
    compute_host_cluster_URL: http://192.168.40.232:31270/api/v1/query
    """
    headers = {'X-Scope-OrgID': cluster_name}
    name =  namespace
    cluster_namespace_container_metrics = {
            'cluster_ns_container_cpu_usage': 'sum(rate(container_cpu_usage_seconds_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container) * 100', 
            'cluster_ns_container_cpu_cfs_periods_total': 'sum(rate(container_cpu_cfs_periods_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)',  
            'cluster_ns_container_cpu_cfs_throttled_periods_total': 'sum(rate(container_cpu_cfs_throttled_periods_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)',  

            'cluster_ns_container_mem_usage_bytes': 'sum(container_memory_usage_bytes{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_mem_max_usage_bytes': 'sum(container_memory_max_usage_bytes{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',  
            'cluster_ns_container_mem_rss_KiB': 'sum(container_memory_rss{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_mem_working_set_bytes': 'sum(container_memory_working_set_bytes{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_mem_cache_KiB': 'sum(container_memory_cache{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_mem_failures_total': 'sum(rate(container_memory_failures_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)',
            'cluster_ns_container_memory_failcnt': 'sum(rate(container_memory_failcnt{namespace="' + name + '", container=~".+", container!="POD"}[60m])) by (container)',

            'cluster_ns_container_fs_inodes_free': 'sum(container_fs_inodes_free{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_fs_inodes_total': 'sum(container_fs_inodes_total{namespace="' + name + '", container=~".+", container!="POD"}) by (container)', 
            'cluster_ns_container_usage_bytes': 'sum(container_fs_usage_bytes{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_fs_reads_total': 'sum(rate(container_fs_reads_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)', 
            'cluster_ns_container_fs_reads_bytes_total': 'sum(rate(container_fs_reads_bytes_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)', 
            'cluster_ns_container_fs_read_seconds_total': 'sum(rate(container_fs_read_seconds_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)', 
            'cluster_ns_container_fs_writes_total': 'sum(rate(container_fs_writes_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)', 
            'cluster_ns_container_fs_writes_bytes_total': 'sum(rate(container_fs_writes_bytes_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)', 
            'cluster_ns_container_fs_write_seconds_total': 'sum(rate(container_fs_write_seconds_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)', 
            
            'cluster_ns_container_status_restarts_total': 'sum(kube_pod_container_status_restarts_total{namespace="' + name + '", container=~".+"}) by (container)', 
            'cluster_ns_container_status_restarts_1h': 'sum(rate(kube_pod_container_status_restarts_total{namespace="' + name + '", container=~".+"}[60m])) by (container)', 
            'cluser_ns_container_status_ready': 'sum(kube_pod_container_status_ready{namespace="' + name + '", container=~".+", job=~"kube-state-metrics"}) by (container)',
            'cluster_ns_container_status_running': 'sum(kube_pod_container_status_running{namespace="' + name + '", container=~".+", job=~"kube-state-metrics"}) by (container)', 
            'cluster_ns_container_status_waiting': 'sum(kube_pod_container_status_running{namespace="' + name + '", container=~".+", job=~"kube-state-metrics"}) by (container)',
            'cluster_ns_container_status_terminated': 'sum(kube_pod_container_status_running{namespace="' + name + '", container=~".+", job=~"kube-state-metrics"}) by (container)',
            }
    
    rows = []
    r0 = requests.get(url = URL, headers = headers, params = {'query': cluster_namespace_container_metrics['cluster_ns_container_cpu_usage']})
    r0_json = r0.json()['data']['result']
    # print(r0_json)
    for result in r0_json:
        l = []
        l.append(result['metric'].get('container', ''))
        rows.append(l)

    for metric_name, metric_value in cluster_namespace_container_metrics.items():
        r1 = requests.get(url = URL, headers = headers, params = {'query': metric_value})
        r1_json = r1.json()['data']['result']
        row = 0
        for result in r1_json:
                l = []
                l.append(result['value'][1])
                rows[row].append(l[0])
                ts = []
                ts.append(time.time())
                rows[row].append(ts[0])
                row = row + 1     
    return rows


URL = "http://192.168.24.20:31179/prometheus/api/v1/query"
metrics_name = ['container', 'cluster_ns_container_cpu_usage', 'cluster_ns_container_cpu_cfs_periods_total', 'cluster_ns_container_cpu_cfs_throttled_periods_total', 'cluster_ns_container_mem_usage_bytes', 'cluster_ns_container_mem_max_usage_bytes', 'cluster_ns_container_mem_rss_KiB', 'cluster_ns_container_mem_working_set_bytes' \
                , 'cluster_ns_container_mem_cache_KiB', 'cluster_ns_container_mem_failures_total', 'cluster_ns_container_memory_failcnt', 'cluster_ns_container_fs_inodes_free' \
                , 'cluster_ns_container_fs_inodes_total', 'cluster_ns_container_usage_bytes', 'cluster_ns_container_fs_reads_total', 'cluster_ns_container_fs_reads_bytes_total', 'cluster_ns_container_fs_read_seconds_total' \
                , 'cluster_ns_container_fs_writes_total','cluster_ns_container_fs_writes_bytes_total', 'cluster_ns_container_fs_write_seconds_total', 'cluster_ns_container_status_restarts_total', 'cluster_ns_container_status_restarts_1h' \
                , 'cluser_ns_container_status_ready', 'cluster_ns_container_status_running', 'cluster_ns_container_status_waiting', 'cluster_ns_container_status_terminated', 'timestamp' ]


cluster_name = "central-cluster"
name_space = "kube-system"

file_name = cluster_name + '_' + name_space + '_container' + '_data.csv'

with open(file_name, 'w') as f:
         write = csv.writer(f)
         write.writerow(metrics_name)

         for seq in range (0, 2):
            data = cluster_namespace_container_query(URL, cluster_name, name_space)
            # print(data)
            write.writerows(data)
            sys.stdout.flush()
            time.sleep(15)
        
minioClient = warehouse_connection()

date = datetime.datetime.now()

path = "cluster-namespace-container/" + str(date.strftime("%Y")) + date.strftime("%m") + date.strftime("%d")
minioClient.fput_object(cluster_name, path, file_name, content_type='application/csv')
os.remove(file_name)


         

