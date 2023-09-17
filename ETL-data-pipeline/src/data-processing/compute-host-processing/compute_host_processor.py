from minio import Minio
import pandas as pd
import joblib
import io

BUCKET = "compute-host"
PREFIX = ""
SAVED_BUCKET = "compute-host-training"
SAVED_BUCKET_PREFIX = ""


def warehouse_connection(): 
    client = Minio("192.168.24.20:30256",
                    access_key="XwMptXNrhYWMHj99",
                    secret_key="Uatsl7MkYaJVrABZAXRTXfQzbzJ9IwlW",
                    secure=False,
                  )
    
    return client # minio_client


def check_objects(minio_client, bucket_name, prefix, objects):
    """
    List unprocessed objects in the Minio bucket.

    Returns:
        List[str]: List of NEW object names in the bucket.
    """
    new_objects = []
    training_objects = list_objects(minio_client, bucket_name, prefix)
    date_names = [i.split("/")[1].split(".")[0] for i in training_objects] # eg: 20230908
    
    for obj in objects:
        if obj.split("/")[1] not in date_names:
            new_objects.append(obj)

    return new_objects


def list_objects(minio_client, bucket_name, prefix):
    """
    List objects in the Minio bucket.

    Returns:
        List[str]: List of object names in the bucket.
    """
    objects = []
    for obj in minio_client.list_objects(bucket_name, prefix, recursive=True):
        objects.append(obj.object_name)

    return objects


def process_data(minio_client, object_name):
    """
    Process data from a specific object in the Minio bucket.

    Args:
        object_name (str): Name of the object to process.
            eg: 'central-cluster_instance_data/20230908'
    Returns:
        list of pd.DataFrame: Processed data as a Pandas DataFrame for each instance.
    """
    COLS = ['cluster_instance_cpu_utilization',
            'cluster_instance_cpu_rate_sum',
            'cluster_instance_load1_per_cpu',
            'cluster_instance_mem_utilization',
            'cluster_instance_netin_bytes_wo_lo',
            'cluster_instance_netin_bytes_total',
            'cluster_instance_netin_drop_wo_lo',
            'cluster_instance_netout_bytes_wo_lo',
            'cluster_instance_netout_bytes_total',
            'cluster_instance_netout_drop_wo_lo',
            'cluster_instance_disk_io_time',
            'cluster_instance_disk_io_time_wght']
    
    csv_name = f'{PREFIX}_{object_name.split("/")[1]}.csv'
    data = minio_client.fget_object(BUCKET, object_name, csv_name)
    df = pd.read_csv(f"./{csv_name}")

    instances = set(df.instance.values)
    scaler = joblib.load("./central_cluster_instance_scaler.joblib")

    df_list = []
    grouped = df.groupby(df.instance)

    for instance in instances:
        temp = grouped.get_group(instance).reset_index(drop=True)
        scaled_df = pd.DataFrame(scaler.transform(temp.drop(['instance', 'timestamp'], axis=1)), columns=COLS)
        scaled_df['instance'] = temp['instance']
        scaled_df['timestamp'] = temp['timestamp']
        df_list.append(scaled_df)
    
    return df_list


def push_bucket(minio_client, df, object_name):
    """
    Save processed data to Minio bucket.

    Args:
        object_name (str): Name of the object to process.
            eg: 'central-cluster_data/20230908'
    Returns:
        True if pushed successfully
        False if pushed unsuccessfully
    """
    instance = list(set(df.instance.values))[0]
    csv_name = f'{SAVED_BUCKET_PREFIX}/{object_name.split("/")[1]}_{instance}.csv' # central-cluster_instance_data_training/20230908_192.168.24.61:9100.csv

    # Convert the DataFrame to a CSV string
    csv_data = df.to_csv(index=False).encode('utf-8')
    csv_data_io = io.BytesIO(csv_data)

    try:
        # Upload the CSV data to the Minio bucket
        minio_client.put_object(SAVED_BUCKET, csv_name, csv_data_io, len(csv_data))
        print(f'Successfully uploaded {object_name} to {SAVED_BUCKET}/{SAVED_BUCKET_PREFIX}')
    except ResponseError as err:
        print(f'Error uploading {object_name} to {SAVED_BUCKET}/{SAVED_BUCKET_PREFIX}: {err}')


if __name__ == "__main__":
    minio_client = warehouse_connection()

    objects = list_objects(minio_client,
                           BUCKET,
                           PREFIX)
    
    new_objects = check_objects(minio_client,
                                SAVED_BUCKET,
                                SAVED_BUCKET_PREFIX,
                                objects)
    
    for obj in new_objects:
        df_list = process_data(minio_client, obj)
        for df in df_list:
            push_bucket(minio_client, df, obj)

