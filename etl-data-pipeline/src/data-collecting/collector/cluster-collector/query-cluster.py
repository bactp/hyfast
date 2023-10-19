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

def create_new_csv(metrics_name):
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    file_name = f"{cluster_name}_data_{current_date}.csv"
    with open(file_name, mode='w', newline='') as f:
            write = csv.writer(f)
            write.writerow(metrics_name)
    return file_name



metrics_name = ['cluster_MemUsage_Gib', 'cluster_CPUUsage_pct', 
                'cluster_FSUsage_U', 'cluster_NetIn_kBs', 'cluster_NetOut_kBs',  
                'cluster_PodCPUUsage_pct', 'cluster_PodMemUsage_Gib', 'cluster_PodNetIn_kBs',
                'cluster_PodNetOutt_kBs', 'timestamp', 'cluster_name']

URL = os.getenv("URL")
cluster_name = os.getenv("CLUSTER_NAME") #declare as name of the cluster in container image

current_day = None
csv_file_name = None


while True:
    """ Query data every 10 seconds """
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
                path = cluster_name + "_data/" + current_day
                minioClient.fput_object(cluster_name, path, csv_file_name, content_type='application/csv')
                print(f"File: {csv_file_name} is uploaded to storage")
                os.remove(csv_file_name)

                csv_file_name = None

            # Create a new CSV file
            csv_file_name = create_new_csv(metrics_name)
            print(f"New file created: {csv_file_name}")

        # Simulate writing data to the CSV file
        with open(csv_file_name, mode='a', newline='') as f:
                    write = csv.writer(f)
                    rows =  []
                    data = cluster_query(URL, cluster_name)
                    rows.append(data)
                    write.writerows(rows)
                    
        current_day = current_date
        time.sleep(10)
    except Exception as e:
            print("reconnecting to endpoints")
            time.sleep(15)