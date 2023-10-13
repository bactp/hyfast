from datetime import timedelta as tdt
import datetime
import os
import numpy as np
import pandas as pd
from minio import Minio

def load_gen(start, stop, seconds) -> list:
    # rng = np.random.RandomState(2023)
    np.random.seed(99)
    rand_load = list(np.random.randint([start], [stop], size=int(seconds/60))) # 15s per request gen
    return rand_load

def warehouse_connection():
    client = Minio("192.168.24.20:30256",
                    access_key="XwMptXNrhYWMHj99",
                    secret_key="Uatsl7MkYaJVrABZAXRTXfQzbzJ9IwlW",
                    secure=False,
    )
    return client
    
load_list = []
load_thresh = [(30, 50),  #0-0:10
                (120, 130),  #0:10-1:30
                (50, 80), #1:30-4:30
                (15, 35),  #4:30-8
                (70, 120), #8-10
                (100, 120),   #10-12:30
                (150, 200),   #12:30-16
                (70, 110), #16-18:30
                (40, 65), #18:30-20:30
                (100, 150), #20:30-22:30
                (150, 200)] #22:30-24
        
time_segment = [(tdt(hours=0), tdt(hours=0, minutes=10)),
                (tdt(hours=0, minutes=10), tdt(hours=1, minutes=30)),
                (tdt(hours=1, minutes=30), tdt(hours=4, minutes=30)),
                (tdt(hours=4, minutes=30), tdt(hours=8)),
                (tdt(hours=8), tdt(hours=10)),
                (tdt(hours=10), tdt(hours=12, minutes=30)),
                (tdt(hours=12, minutes=30), tdt(hours=16)),
                (tdt(hours=16), tdt(hours=18, minutes=30)),
                (tdt(hours=18, minutes=30), tdt(hours=20, minutes=30)),
                (tdt(hours=20, minutes=30), tdt(hours=22, minutes=30)),
                (tdt(hours=22, minutes=30), tdt(hours=24))]

for ts, lt in zip(time_segment, load_thresh):
    sec = (ts[1] - ts[0]).seconds
    load_list.extend(load_gen(lt[0], lt[1], sec))
    


cluster_name = os.getenv("CLUSTER_NAME")
name_space = os.getenv("NAME_SPACE")

# cluster_name = "data-center2"
# name_space = "sock-shop"

now = datetime.datetime.now()
current_date = now.strftime("%Y%m%d")
csv_file_name = "num_reqs.csv"

load_df = pd.DataFrame(load_list, columns=['num_reqs'])
load_df.to_csv(csv_file_name, index=0)

minioClient = warehouse_connection()
path = cluster_name + "_" + name_space + "_request_gen/" + current_date
minioClient.fput_object(cluster_name, path, csv_file_name, content_type='application/csv')



    
    

    
    





