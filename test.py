import pandas as pd
import os

exchange_path = '/mnt/exchange/'
basepath = os.path.join(exchange_path, 'ASR Management/netflix/')
jsonpath = os.path.join(basepath, 'script_folder/json/')
g2p_path = basepath + "script_folder/output/g2p.tsv"


g2p = pd.read_csv(g2p_path)

g2p = g2p['transcriptions'].str.split('\t', expand=True)

g2p.columns = ['g2p_{}'.format(i) for i in range(1, g2p.shape[1] + 1)]

g2p = g2p.iloc[:,:10]

print(g2p)