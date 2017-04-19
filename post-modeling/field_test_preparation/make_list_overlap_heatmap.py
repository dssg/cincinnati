import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import sklearn_evaluation
from sklearn_evaluation.plots import compute_similarity
from lib_cinci.config import load 
import sqlalchemy
from sqlalchemy import create_engine

connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'\
      .format(**connparams)
engine = create_engine(uri)

query = '''
        SELECT model_group, subset, reason
        FROM model_results.all_top_k
        JOIN model_results.model_reasons
u       USING (model_group)
        GROUP BY 1,2,3;
        '''

top_models = pd.read_sql(query, engine)
all_top_k = pd.read_sql_table('all_top_k', engine, 
                              schema='model_results', 
                              index_col=['model_group','subset'])
engine.dispose()

model_groups = top_models.model_group
reasons = top_models.reason 
subsets = top_models.subset

top_k = {}
for model_group in model_groups.unique():
    for subset in subsets.unique():
        top_k[str(model_group) + str(subset)] = all_top_k.loc[model_group, subset]

model_groups = model_groups.map(str)
top_k_labels = [l[0] + ' (' + l[1] + ') - \n ' + l[2] for l in zip(reasons,model_groups,subsets)]
top_k_parcels = [p.parcel_id.unique() for p in top_k.values()] 
d = dict(zip(top_k_labels, top_k_parcels))
prediction_matrix = pd.DataFrame.from_dict(d)

df = compute_similarity(prediction_matrix)
cmap = sns.cubehelix_palette(dark=0, light=1, start=.5, rot=-.75, as_cmap=True)

f,ax = plt.subplots(figsize=(80, 60))

ax = sns.heatmap(df,linewidths=0.5, vmin=0, vmax=1, cmap=cmap)
plt.xticks(rotation=45, ha='right', fontsize=24)
plt.yticks(fontsize=24)

ax.figure.savefig('list_overlap_heatmap.png')
