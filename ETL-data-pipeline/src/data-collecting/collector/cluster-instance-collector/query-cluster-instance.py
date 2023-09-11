import requests
import json
import time, datetime
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

def create_new_csv(metrics_name):
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    file_name = f"{cluster_name}_instance_data_{current_date}.csv"
    with open(file_name, mode='w', newline='') as f:
            write = csv.writer(f)
            write.writerow(metrics_name)
    return file_name



metrics_name = ['instance', 'cluster_instance_cpu_utilization', 
                'cluster_instance_cpu_rate_sum', 'cluster_instance_load1_per_cpu', 
                'cluster_instance_mem_utilization', 'cluster_instance_netin_bytes_wo_lo', 
                'cluster_instance_netin_bytes_total', 'cluster_instance_netin_drop_wo_lo',
                'cluster_instance_netout_bytes_wo_lo', 'cluster_instance_netout_bytes_total',
                'cluster_instance_netout_drop_wo_lo', 'cluster_instance_disk_io_time', 
                'cluster_instance_disk_io_time_wght', 'timestamp']


URL = os.getenv("URL")
cluster_name = os.getenv("CLUSTER_NAME") 

current_day = None
csv_file_name = None

while True:
    """ Query data every 10 seconds """
    
    now = datetime.datetime.now()
    current_date = now.strftime("%Y%m%d")

    # Check if the day has changed
    if current_date != current_day:
        if csv_file_name:
            print(f"Closing file: {csv_file_name}")
            current_day = current_date

            #Upload to storage
            minioClient = warehouse_connection()
            path =  cluster_name + "_instance_data/" + current_day
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
                data = cluster_instance_query(URL, cluster_name)
                write.writerows(data)
                
    current_day = current_date
    time.sleep(10)



         

