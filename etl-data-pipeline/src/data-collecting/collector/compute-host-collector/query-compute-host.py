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
            'host_mem_utilization': 'sum(instance:node_memory_utilisation:ratio) by (instance)',
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
                # ts = []
                # ts.append(time.time())
                # rows[row].append(ts[0])
                row = row + 1
    for row in rows:
        ts = str(time.time())
        row.append(ts)     
    return rows


def create_new_csv(metrics_name):
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    file_name = f"compute_host_data_{current_date}.csv"
    with open(file_name, mode='w', newline='') as f:
            write = csv.writer(f)
            write.writerow(metrics_name)
    return file_name


URL = os.getenv("URL")
# URL = "http://192.168.24.20:31179/prometheus/api/v1/query"
metrics_name = ['instance', 'host_cpu_utilization', 'host_cpu_rate_sum', 
                'host_load1_per_cpu', 'host_mem_utilization', 'host_netin_bytes_wo_lo',  
                'host_netin_bytes_total', 'host_netin_drop_wo_lo', 'host_netout_bytes_wo_lo',
                'host_netout_bytes_total', 'host_netout_drop_wo_lo', 'host_disk_io_time',
                'host_disk_io_time_wght', 'timestamp']


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
                path = current_day
                minioClient.fput_object('compute-host', path, csv_file_name, content_type='application/csv')
                print(f"File: {csv_file_name} is uploaded to storage")
                os.remove(csv_file_name)

                csv_file_name = None

            # Create a new CSV file
            csv_file_name = create_new_csv(metrics_name)
            print(f"New file created: {csv_file_name}")

        # Simulate writing data to the CSV file
        with open(csv_file_name, mode='a', newline='') as f:
                    write = csv.writer(f)
                    data = compute_host_query(URL)
                    write.writerows(data)
                    
        current_day = current_date
        time.sleep(10)
    except Exception as e:
            print("reconnecting to endpoints")
            time.sleep(15)





         

