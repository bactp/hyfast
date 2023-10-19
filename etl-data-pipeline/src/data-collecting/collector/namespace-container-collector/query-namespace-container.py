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
            'cluster_ns_container_cpu_usage': 'sum(rate(container_cpu_usage_seconds_total{namespace="' + name + '", container=~".+", container!="POD"}[5m])) by (container) * 100', 
            # 'cluster_ns_container_cpu_cfs_periods_total': 'sum(rate(container_cpu_cfs_periods_total{namespace="' + name + '", container=~".+", container!="POD"}[5m])) by (container)',  #
            # 'cluster_ns_container_cpu_cfs_throttled_periods_total': 'sum(rate(container_cpu_cfs_throttled_periods_total{namespace="' + name + '", container=~".+", container!="POD"}[5m])) by (container)',  #

            'cluster_ns_container_mem_usage_bytes': 'sum(container_memory_usage_bytes{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_mem_max_usage_bytes': 'sum(container_memory_max_usage_bytes{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',  
            'cluster_ns_container_mem_rss_KiB': 'sum(container_memory_rss{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_mem_working_set_bytes': 'sum(container_memory_working_set_bytes{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_mem_cache_KiB': 'sum(container_memory_cache{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_mem_failures_total': 'sum(rate(container_memory_failures_total{namespace="' + name + '", container=~".+", container!="POD"}[5m])) by (container)',
            'cluster_ns_container_memory_failcnt': 'sum(rate(container_memory_failcnt{namespace="' + name + '", container=~".+", container!="POD"}[60m])) by (container)',

            'cluster_ns_container_fs_inodes_free': 'sum(container_fs_inodes_free{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_fs_inodes_total': 'sum(container_fs_inodes_total{namespace="' + name + '", container=~".+", container!="POD"}) by (container)', 
            'cluster_ns_container_usage_bytes': 'sum(container_fs_usage_bytes{namespace="' + name + '", container=~".+", container!="POD"}) by (container)',
            'cluster_ns_container_fs_reads_total': 'sum(rate(container_fs_reads_total{namespace="' + name + '", container=~".+", container!="POD"}[5m])) by (container)', 
            # 'cluster_ns_container_fs_reads_bytes_total': 'sum(rate(container_fs_reads_bytes_total{namespace="' + name + '", container=~".+", container!="POD"}[5m])) by (container)', #
            'cluster_ns_container_fs_read_seconds_total': 'sum(rate(container_fs_read_seconds_total{namespace="' + name + '", container=~".+", container!="POD"}[5m])) by (container)', 
            'cluster_ns_container_fs_writes_total': 'sum(rate(container_fs_writes_total{namespace="' + name + '", container=~".+", container!="POD"}[30m])) by (container)', 
            # 'cluster_ns_container_fs_writes_bytes_total': 'sum(rate(container_fs_writes_bytes_total{namespace="' + name + '", container=~".+", container!="POD"}[5m])) by (container)', #
            'cluster_ns_container_fs_write_seconds_total': 'sum(rate(container_fs_write_seconds_total{namespace="' + name + '", container=~".+", container!="POD"}[5m])) by (container)', 
            
            'cluster_ns_container_status_restarts_total': 'sum(kube_pod_container_status_restarts_total{namespace="' + name + '", container=~".+"}) by (container)', 
            'cluster_ns_container_status_restarts_1h': 'sum(rate(kube_pod_container_status_restarts_total{namespace="' + name + '", container=~".+"}[60m])) by (container)', 
            'cluser_ns_container_status_ready': 'sum(kube_pod_container_status_ready{namespace="' + name + '", container=~".+", job=~"kube-state-metrics"}) by (container)',
            'cluster_ns_container_status_running': 'sum(kube_pod_container_status_running{namespace="' + name + '", container=~".+", job=~"kube-state-metrics"}) by (container)', 
            'cluster_ns_container_status_waiting': 'sum(kube_pod_container_status_running{namespace="' + name + '", container=~".+", job=~"kube-state-metrics"}) by (container)',
            'cluster_ns_container_status_terminated': 'sum(kube_pod_container_status_running{namespace="' + name + '", container=~".+", job=~"kube-state-metrics"}) by (container)'
            }
    
    rows = []
    r0 = requests.get(url = URL, headers = headers, params = {'query': cluster_namespace_container_metrics['cluster_ns_container_cpu_usage']})
    r0_json = r0.json()['data']['result']
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
                # ts = []
                # ts.append(time.time())
                # rows[row].append(ts[0])
                row = row + 1     
    for row in rows:
        ts = str(time.time())
        row.append(ts)
    return rows


def create_new_csv(metrics_name, cluster_name, name_space):
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    file_name = f"{cluster_name}_{name_space}_container_data_{current_date}.csv"
    with open(file_name, mode='w', newline='') as f:
            write = csv.writer(f)
            write.writerow(metrics_name)
    return file_name


metrics_name = ['container',
                'cluster_ns_container_cpu_usage',
                # 'cluster_ns_container_cpu_cfs_periods_total', 
                # 'cluster_ns_container_cpu_cfs_throttled_periods_total',
                'cluster_ns_container_mem_usage_bytes', 
                'cluster_ns_container_mem_max_usage_bytes',
                'cluster_ns_container_mem_rss_KiB', 
                'cluster_ns_container_mem_working_set_bytes',
                'cluster_ns_container_mem_cache_KiB', 
                'cluster_ns_container_mem_failures_total',
                'cluster_ns_container_memory_failcnt', 
                'cluster_ns_container_fs_inodes_free',
                'cluster_ns_container_fs_inodes_total', 
                'cluster_ns_container_usage_bytes',
                'cluster_ns_container_fs_reads_total', 
                # 'cluster_ns_container_fs_reads_bytes_total',
                'cluster_ns_container_fs_read_seconds_total',
                'cluster_ns_container_fs_writes_total',
                # 'cluster_ns_container_fs_writes_bytes_total', 
                'cluster_ns_container_fs_write_seconds_total',
                'cluster_ns_container_status_restarts_total', 
                'cluster_ns_container_status_restarts_1h',
                'cluser_ns_container_status_ready', 
                'cluster_ns_container_status_running',
                'cluster_ns_container_status_waiting', 
                'cluster_ns_container_status_terminated',
                'timestamp' ]


URL = os.getenv("URL")
cluster_name =  os.getenv("CLUSTER_NAME") #declare as name of the cluster in container image
name_space = os.getenv("NAME_SPACE") #declare as name of namespace in container image

# URL = "http://192.168.24.20:31179/prometheus/api/v1/query"
# cluster_name = "data-center1"
# name_space = "sock-shop"

current_day = None
csv_file_name = None


while True:
    try: 
        now = datetime.datetime.now()
        current_date = now.strftime("%Y%m%d")

        # Check if the day has changed
        if current_date != current_day:
            if csv_file_name:
                print(f"Closing file: {csv_file_name}")
                current_day = current_date

                #Upload to storage
                minioClient = warehouse_connection()
                path = cluster_name + "_" + name_space + "_container_data/" + current_day
                minioClient.fput_object(cluster_name, path, csv_file_name, content_type='application/csv')
                print(f"File: {csv_file_name} is uploaded to storage")
                os.remove(csv_file_name)

                csv_file_name = None

            # Create a new CSV file
            csv_file_name = create_new_csv(metrics_name, cluster_name, name_space)
            print(f"New file created: {csv_file_name}")

        # Simulate writing data to the CSV file
        with open(csv_file_name, mode='a', newline='') as f:
                    write = csv.writer(f)
                    data = cluster_namespace_container_query(URL, cluster_name, name_space)
                    write.writerows(data)
                    
        current_day = current_date
        time.sleep(10)
    except Exception as e:
            print("reconnecting to endpoints")
            time.sleep(15)


         

