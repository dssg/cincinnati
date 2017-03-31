import pandas as pd
import os
from lib_cinci.train_and_predict import main, predict_on_date, train_on_config

k = 7500 # top 5% of parcels in Cincinnati

top_models = pd.read_csv('top_model_reason_lookup.csv')
model_groups = top_models.model_group.values 

models_grouped = pd.read_csv('model-results-grouped.csv', index_col='group_number')
parcel_info = pd.read_csv('parcels-with-neighborhood-info.csv', index_col='parcel_id')

# get model ids and names from model columns
model_id_columns = [col for col in list(models_grouped) if col.startswith('model_id')]
model_name_columns = [col for col in list(models_grouped) if col.startswith('name')]

all_top_k = {}
all_feature_importances = {}

for model_group in model_groups:
    model_id = models_grouped.loc[model_group, model_id_columns].dropna()[0]
    model_name = models_grouped.loc[model_group, model_name_columns].dropna()[0]

    model_group = str(model_group)

    # Retrain model and get predictions on all parcels
    trained_model_df, trained_model_dict = main(model_id=model_id, 
                                                train_end_date='30Aug2016',  
                                                prediction_schema='features_31aug2016',
                                                return_features=True, 
                                                return_fitted=True)       
    trained_model_df.sort_values('prediction', ascending=False, inplace=True)

    # Add neighborhood metrics for each parcel 
    model_predictions = trained_model_df[['prediction']].join(parcel_info)
    all_top_k[model_group] = model_predictions.head(7500)

    # Get feature importances (or coefficients for Logistic Regression)
    if model_name == 'LogisticRegression':
        feature_importances = pd.DataFrame(data=[trained_model_df.columns[:-1],
                                                 trained_model_dict['model'].coef_]).T

    else:
        feature_importances = pd.DataFrame(data = [trained_model_df.columns[:-1], 
                                                   trained_model_dict['model'].feature_importances_]).T

    feature_importances.columns = ['feature', 'feature_importance']
    feature_importances['model_group'] = model_group

    all_feature_importances[model_group] = feature_importances

    # Get list of top k parcels below median ID
    inspection_density_median = model_predictions.inspection_density.median()
    median_mask = model_predictions.inspection_density < inspection_density_median
    below_median_ID = model_predictions[median_mask].head(k)
    all_top_k[model_group + ' Below Median ID'] = below_median_ID

    # Get list of top k parcels below first quartile ID
    inspection_density_first_quartile = model_predictions.inspection_density.quantile(0.25)
    first_quartile_mask = model_predictions.inspection_density < inspection_density_first_quartile
    below_quartile_ID = model_predictions[first_quartile_mask].head(k)
    all_top_k[model_group + ' Below First Quartile ID'] = below_quartile_ID
    
all_top5 = pd.concat(all_top_k.values(), keys=all_top_k.keys())
all_top5['violations_per_house'] = all_top5['violation_rate'] * all_top5['inspection_density'] 
all_top5.to_csv('all_top5.csv')

all_features_csv = pd.concat(all_feature_importances.values())
all_features_csv.set_index(['feature','model_group']).unstack().to_csv('feature_importances.csv')

