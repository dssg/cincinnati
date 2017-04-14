import pandas as pd
import numpy as np
import sklearn
import os
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import sklearn_evaluation
from sklearn_evaluation.plots import compute_similarity
import yaml
from sklearn_evaluation.Logger import Logger
from lib_cinci.config import load 

folder = os.environ['ROOT_FOLDER']
name = 'config.yaml'
path = "%s/%s" % (folder, name)
f = open(path, 'r')
text = f.read()
main_yaml = yaml.load(text)
logger = Logger(host=main_yaml['logger']['uri'],
                db=main_yaml['logger']['db'],
                collection=main_yaml['logger']['collection'])

connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'\
      .format(**connparams)
libpq_uri = 'dbname={database} user={user} host={host} password={password} port={port}'\
      .format(**connparams)

all_top_k = pd.read_sql_table('all_top_k', con=uri, schema='model_results', index_col='model_group')
top_models = pd.read_sql_table('model_reasons', con=uri, schema='model_results')

model_groups = top_models.model_group
reasons = top_models.reason 

top_k = {}
for model_group in model_groups:
    top_k[model_group] = all_top_k.loc[model_group]

model_groups = model_groups.map(str)
top_k_labels = [l[0] + ' (' + l[1] + ')' for l in zip(reasons,model_groups)]
top_k_parcels = [p.parcel_id.unique() for p in top_k.values()] 
d = dict(zip(top_k_labels, top_k_parcels))
prediction_matrix = pd.DataFrame.from_dict(d)

df = compute_similarity(prediction_matrix)
cmap = sns.cubehelix_palette(dark=0, light=1, start=.5, rot=-.75, as_cmap=True)

f,ax = plt.subplots(figsize=(20, 15))

ax = sns.heatmap(df,linewidths=0.5, vmin=0, vmax=1, cmap=cmap)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)

ax.figure.savefig('list_overlap_heatmap.png')
