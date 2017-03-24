import pandas as pd
#import numpy as np
#import sklearn
import os

import lib_cinci.train_and_predict
from lib_cinci.train_and_predict import main, predict_on_date, train_on_config
#from lib_cinci import dataset
#from lib_cinci.config import load

output_folder = os.environ['OUTPUT_FOLDER']

#specify which models you want to retrain
model_groups = [18711, 1120, 14613, 5716, 
                27039, 7111, 28879, 26523, 
                1309, 12547, 10062, 28108, 
                11814, 7068, 29230, 25683, 7520]

k = 7500 # top 5% of parcels

#models = pd.read_csv('model-results-grouped.csv')
#model_id_cols = [col for col in list(models) if col.startswith('MODELID')]
#model_name_cols = [col for col in list(models) if col.startswith('name')]
all_models = pd.read_csv('model-results-2017-03-23.csv', index_col='model_id')

all_top_k = {}
model_ids = ['585b70bcba2d6c88519e89fd']
parcel_info = pd.read_csv('parcels-with-neighborhood-info.csv', index_col='parcel_id')

#for m in model_groups: 
for model_id in model_ids:
#    model_group = str(m)
    model_group = model_id
    model_name = all_models.loc[model_id, 'name']

#    model_id = str(models[model_id_cols].iloc[m].dropna().values[0])

    # Retrain model and get predictions on all parcels
    trained_model_df, trained_model_dict = main(model_id=model_id, 
                                                train_end_date='30Aug2016',  
                                                prediction_schema='features_31aug2016', # todo : make variable
                                                return_features=True, 
                                                return_fitted=True)       
    trained_model_df.sort_values('prediction', ascending=False, inplace=True)

    # Add neighborhood metrics for each parcel and save to CSV
    model_predictions = trained_model_df[['prediction']].join(parcel_info)
    all_top_k[model_group] = model_predictions.head(7500)

    # Save feature importances to CSV
    if model_name == 'LogisticRegression':
        feature_importances = pd.DataFrame(data=[trained_model_df.columns[:-1],
                                           trained_model_dict['model'].coef_]).T

    else:
        feature_importances = pd.DataFrame(data = [trained_model_df.columns[:-1], 
                                               trained_model_dict['model'].feature_importances_]).T

    feature_importances.columns = ['feature', 'feature_importance']
    output_path = os.path.join(output_folder, 'feature_importances', 'feature_importances_' + model_group + '.csv')
    feature_importances.to_csv(output_path)
    
    # Get list of top k parcels below median ID
    inspection_density_median = model_predictions['inspection_density'].median()
    median_mask = model_predictions.inspection_density < inspection_density_median
    below_median_ID = model_predictions[median_mask].head(k)
    all_top_k[model_group + ' Below Median ID'] = below_median_ID

    # Get list of top k parcels below first quartile ID
    inspection_density_first_quartile = model_predictions.inspection_density.quantile(0.25)
    first_quartile_mask = model_predictions.inspection_density < inspection_density_first_quartile
    below_quartile_ID = model_predictions[first_quartile_mask].head(k)
    all_top_k[model_group + ' Below First Quaritle ID'] = below_quartile_ID
    

all_top5 = pd.concat(all_top_k.values())
all_top5['violations_per_house'] = all_top5['violation_rate'] * all_top5['inspection_density'] 
all_top5.to_csv('all_top5.csv')

# make feature crosstabs

#query = '''
#        SELECT DISTINCT (table_name) 
#        FROM information_schema.tables 
#        WHERE table_schema = 'features_31aug2016';
#        '''
#all_tables = pd.read_sql(query, engine)

#all_features = {}

#for t in list(all_tables.table_name):

#    query = 'SELECT * FROM features_31aug2016.{table};'.format(table=t)
    
 #   features = pd.read_sql(query, engine, index_col = 'parcel_id')
 #   features.columns = [t + '.' + str(col) for col in features.columns]
 #   all_features[t] = features

# combine all features
#all_features = pd.concat(all_features.values())

# get mean over all parcels
#all_features_mean = all_features.mean(axis=0)
# add a column for model group (all parcels doesn't have one)
#all_features_mean = all_features_mean.append(pd.Series([1.0], index=['model_group']))

#all_features_mean_df = all_features_mean.to_frame().T

#feature_averages = {}

#for m in model_groups: 
    #list_name = str(m)
    
 #   model_features = all_features[all_features.index.isin(top_k[list_name].index)].mean(axis=0)
   # model_features = model_features.to_frame().T
  #  
#    feature_averages[list_name + ' Top 5'] = model_features
#    feature_averages[list_name + ' Top 5']['model_group'] = model_num
#    feature_averages[list_name + ' Top 5']['subset'] = 'Top 5 Average'
#    feature_averages[list_name + ' Top 5']['list'] = 'All Parcels'
    
#    feature_averages[list_name + ' Ratio'] = model_features.divide(all_features_mean_df, axis=1)
#    feature_averages[list_name + ' Ratio']['model_group'] = model_num
#    feature_averages[list_name + ' Ratio']['subset'] = 'Ratio'
#    feature_averages[list_name + ' Ratio']['list'] = 'All Parcels'

#crosstabs = pd.concat(feature_averages.values())
#crosstabs = crosstabs.append(all_features_mean_df)
#crosstabs.set_index(['model_group','list','subset'], inplace=True)
#crosstabs.reset_index(inplace=True)

#crosstabs['new_index'] = crosstabs['model_group'].map(int).map(str) + ' ' + crosstabs['list'] + ' ' + crosstabs['subset']
#crosstabs.set_index('new_index', inplace=True)
#crosstabs.T.to_csv('feature_crosstabs.csv')
