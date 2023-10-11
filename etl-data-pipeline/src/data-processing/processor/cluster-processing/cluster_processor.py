from minio import Minio
import pandas as pd
import joblib
import io

BUCKET = "central-cluster"
PREFIX = "central-cluster_data"
SAVED_BUCKET = "central-cluster-training"
SAVED_BUCKET_PREFIX = "central-cluster_data_training"


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
    date_names = set(date_names)
    
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
            eg: 'central-cluster_data/20230908'
    Returns:
        pd.DataFrame: Processed data as a Pandas DataFrame.
    """
    COLS = ['cluster_MemUsage_Gib',
            'cluster_CPUUsage_pct',
            'cluster_FSUsage_U',
            'cluster_NetIn_kBs',
            'cluster_NetOut_kBs',
            'cluster_PodCPUUsage_pct',
            'cluster_PodMemUsage_Gib',
            'cluster_PodNetIn_kBs',
            'cluster_PodNetOutt_kBs']
    
    csv_name = f'{PREFIX}_{object_name.split("/")[1]}.csv'
    data = minio_client.fget_object(BUCKET, object_name, csv_name)
    df = pd.read_csv(f"./{csv_name}")
    df = df.fillna(0)
    
    scaler = joblib.load("./central_cluster_scaler.joblib")

    scaled_df = pd.DataFrame(scaler.transform(df.drop(['cluster_name', 'timestamp'], axis=1)), columns=COLS)
    scaled_df['cluster_name'] = df['cluster_name']
    scaled_df['timestamp'] = df['timestamp']

    return scaled_df


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
    csv_name = f'{SAVED_BUCKET_PREFIX}/{object_name.split("/")[1]}.csv' # central-cluster_data_training/20230908.csv

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
        df = process_data(minio_client, obj)
        push_bucket(minio_client, df, obj)

