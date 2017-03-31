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

all_top5 = pd.read_csv('all_top5.csv', index_col=0)
top_models = pd.read_csv('top_model_reason_lookup.csv')
model_groups = top_models.model_group.map(str)

top_k = {}
for model_group in model_groups:
    top_k[model_group] = all_top5.loc[model_group]

d = {k: v.parcel_id.values for k,v in top_k.iteritems()}
top_k_dict = {top_k_labels[k]: v for k, v in d.items()}
prediction_matrix = pd.DataFrame.from_dict(top_k_dict)
df = compute_similarity(prediction_matrix)
cmap = sns.cubehelix_palette(dark=0, light=1, start=.5, rot=-.75, as_cmap=True)

f,ax = plt.subplots(figsize=(20, 15))

ax = sns.heatmap(df,linewidths=0.5, vmin=0, vmax=1, cmap=cmap)
plt.xticks(rotation=45, ha='right')
ax.figure.savefig('list_overlap_heatmap.png')
