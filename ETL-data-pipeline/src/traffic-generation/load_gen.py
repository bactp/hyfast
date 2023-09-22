from datetime import timedelta as tdt
import numpy as np
import pandas as pd

def load_gen(start, stop, seconds) -> list:
    # rng = np.random.RandomState(2023)
    np.random.seed(99)
    rand_load = list(np.random.randint([start], [stop], size=int(seconds/15))) # 15s per request gen
    return rand_load


load_list = []

load_thresh = [(200, 516),
               (201, 271),
               (271, 501),
               (501, 981),
               (270, 979),
               (271, 516),
               (516, 961),
               (317, 959)]

time_segment = [(tdt(hours=0), tdt(hours=4, minutes=30)),
                (tdt(hours=4, minutes=30), tdt(hours=8)),
                (tdt(hours=8), tdt(hours=10)),
                (tdt(hours=10), tdt(hours=12, minutes=30)),
                (tdt(hours=12, minutes=30), tdt(hours=16)),
                (tdt(hours=16), tdt(hours=20, minutes=30)),
                (tdt(hours=20, minutes=30), tdt(hours=22, minutes=50)),
                (tdt(hours=22, minutes=50), tdt(hours=24))
                ]

for ts, lt in zip(time_segment, load_thresh):
    sec = (ts[1] - ts[0]).seconds
    load_list.extend(load_gen(lt[0], lt[1], sec))

load_df = pd.DataFrame(load_list, columns=['num_reqs'])
load_df.to_csv('./num_reqs.csv', index=0)
print(load_df)
print(len(load_list), load_list[0], load_list[10], load_list[-1])


