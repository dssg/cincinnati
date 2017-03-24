import pandas as pd
import os
from lib_cinci.train_and_predict import main, predict_on_date, train_on_config

output_folder = os.environ['OUTPUT_FOLDER']

#specify which models you want to retrain
model_groups = [18711, 1120, 14613, 5716, 
                27039, 7111, 28879, 26523, 
                1309, 12547, 10062, 28108, 
                11814, 7068, 29230, 25683, 7520]

k = 7500 # top 5% of parcels

all_models = pd.read_csv('model-results-2017-03-23.csv', index_col='model_id')

all_top_k = {}
model_ids = ['585b70bcba2d6c88519e89fd']
parcel_info = pd.read_csv('parcels-with-neighborhood-info.csv', index_col='parcel_id')

#for m in model_groups: 
for model_id in model_ids:
#    model_group = str(m)
    model_group = model_id
    model_name = all_models.loc[model_id, 'name']

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
    output_path = os.path.join(output_folder, 
                               'feature_importances', 
                               'feature_importances_' + model_group + '.csv')
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

