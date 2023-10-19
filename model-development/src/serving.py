import json
import requests
from src.utils import *

def message(d: dict):
    """
    Create message for root cause resulting and recovery triggering
    """
    tmp_lst = [k for k, _ in d.items()]
    unq_prefix = set([k.split('_')[0] for k in tmp_lst])
    tmp_d = {}
    for k in unq_prefix:
        tmp_d[k] = 0
    
    for k in unq_prefix:
        for i in tmp_lst:
            if i.startswith(k):
                tmp_d[k] += 1
    sorted_d = {k: v for k, v in sorted(tmp_d.items(), key=lambda item: item[1], reverse=True)}
    topk_d = dict(list(sorted_d.items())[0: 1])
    msg = list(topk_d.keys())[0]
    return msg


def serving_by_instance(instance_list, model):
    """
    Make prediction real-time and trigger recovery
    """
    incident_list = []
    incident_df_list = []
    for instance in instance_list:
        data =  data_stream_instance(instance)
        data_df =  pd.DataFrame([data])
        data_df = data_df.reindex(columns=sorted(data_df.columns))
        feature = data_df.loc[:, ~data_df.columns.isin(['timestamp', 'label'])].copy()
        # feature = tp_preprocess_data(df=feature) 

        abnormal_points = predict(model=model, df=feature)
        if abnormal_points['abnormal_score'].item() == 1: # 1: normal, 0: abnormal
            print(time.strftime('%X %x %Z') + ": Anomalous Predicted !!!")
            incident_list.append(instance)
            incident_df_list.append(feature)
    
    return incident_list, incident_df_list

def prediction_mess(incident_cluster):
    # if len(incident_cluster)==0:
    #     pass
    # else:
    #     predict_mess = {
    #                    "data": incident_cluster
    #                    }
        # incident_cluster = "edge-sample-small-01"
        incident_cluster = "abc"
    #     # request_body = json.dumps(predict_mess, indent=4)
    #     print(time.strftime('%X %x %Z') + ": Warning signal")
    #     try:
    #         send_request("http://192.168.40.114:9999/rca/warning", predict_mess)
    #     except:
    #         pass
        
        predict_mess = {
                       "data": incident_cluster
                       }
        # request_body = json.dumps(predict_mess, indent=4)
        print(time.strftime('%X %x %Z') + ": Warning signal")
        try:
            send_request("http://192.168.40.114:9999/rca/warning", predict_mess)
        except:
            print("Err")



def serving_rca(model, data_df: pd.DataFrame, feature_idx: dict):
    """
    Make detection real-time and root cause analysis
    """
    data_df = data_df.reindex(columns=sorted(data_df.columns))
    feature = data_df.loc[:, ~data_df.columns.isin(['timestamp', 'label', 'id'])].copy()

    abnormal_points = predict(model=model, df=feature)

    add_label = visualize(predictions=abnormal_points, df=feature, cols=list(feature.columns))

    # add_label = add_label[add_label['abnormal_score'] == 0]
    # add_label = add_label[add_label['abnormal_score'] == 1]
    arr = add_label.drop(['abnormal_score'], axis=1).to_numpy()
    t = top_map(model=model, k=100000, arr=arr)
    name_mapping = map_feature_name(d=t[0], feature_index=feature_idx)
    # print(name_mapping)

    root_observed = {
        "status": "Incident detected !!!",
        "potential_root_cause": name_mapping
    }
    return root_observed
