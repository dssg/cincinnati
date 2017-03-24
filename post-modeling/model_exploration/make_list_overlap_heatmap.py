import pandas as pd
import numpy as np
import sklearn
import os

import seaborn as sns
import matplotlib.pyplot as plt

top_k_keys = {10062: 'ID (10062)', 
              12547: 'ID (12547)',  
              7111: 'ID (7111)',
             28108: 'ID (28108)', 
             11814: 'ID (11814)',
              18711: 'P@5 (18711)',
              1120: 'P@5 (1120)',
              14613: 'P@5 (14613)',
              5716: 'P@5 (5716)',
              7520: 'All 3 (7520)',
              1309: 'All 3 (1309)',
              26523: 'All 3 (26523)',
              28879: 'All 3 (28879)',
              27039: 'VR (27039)',
              7068: 'VR (7068)',
              29230: 'VR (29230)',
              25683: 'VR (25683)'
             }


d = {k: v.index.values for k,v in top_k.iteritems()}
top_k_dict = {top_k_keys[k]: v for k, v in d.items()}
prediction_matrix = pd.DataFrame.from_dict(top_k_dict)
df = compute_similarity(prediction_matrix)

cmap = sns.cubehelix_palette(dark=0, light=1, start=.5, rot=-.75, as_cmap=True)

f,ax = plt.subplots(figsize=(20, 15))

ax = sns.heatmap(df,linewidths=0.5, vmin=0, vmax=1, cmap=cmap)
plt.xticks(rotation=45, ha='right')
ax.figure.savefig('percent_similarity_top' + str(p) + '_' + date_tag)
