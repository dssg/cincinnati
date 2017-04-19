import pandas as pd
import os
from lib_cinci.train_and_predict import main, predict_on_date, train_on_config
from lib_cinci.config import load
from sklearn_evaluation.Logger import Logger
import yaml
from sqlalchemy import create_engine
import sys

validation_schema = sys.argv[1]
space_delta = sys.argv[2]
time_delta = sys.argv[3]

connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'\
      .format(**connparams)
engine = create_engine(uri)

k = 7500 # top 5% of parcels in Cincinnati

output_folder = os.environ['OUTPUT_FOLDER']
path_to_feature_importances = os.path.join(output_folder, 
                                          'feature_importances.csv')
path_to_all_top_k = os.path.join(output_folder, 'all_top_k.csv')

top_models = pd.read_sql_table('model_reasons', engine,
                               schema='model_results')
model_groups = top_models.model_group.values

models_grouped = pd.read_sql_table('model_groups', engine,
                                    schema='model_results')

all_models = pd.read_sql_table('all_models', engine,
                                schema='model_results', 
                                index_col='model_id')

neighborhood_table = 'neighborhood_score_' + space_delta + '_' + time_delta
neighborhood = pd.read_sql_table(neighborhood_table,
                                 engine,
                                 schema=validation_schema,
                                 index_col='parcel_id')

engine.dispose()

parcel_info = pd.DataFrame()
parcel_info['inspection_density'] = neighborhood['unique_inspections']/\
                                    neighborhood['houses']
parcel_info['violation_rate'] = neighborhood['unique_violations']/\
                                neighborhood['unique_inspections']
parcel_info['violations_per_house'] = neighborhood['unique_violations']/\
                                      neighborhood['houses']

all_top_k = {}
all_feature_importances = {}

for model_group in model_groups:
    model_id = models_grouped.loc[model_group, 'model_id']
    model_name = all_models.loc[model_id, 'model_name']
    model_group = str(model_group)

    # Retrain model and get predictions on all parcels
    trained_model_df, trained_model_dict = main(model_id=model_id, 
                                                train_end_date='30Aug2016',  
                                                prediction_schema=validation_schema,
                                                return_features=True, 
                                                return_fitted=True)       
    trained_model_df.sort_values('prediction', ascending=False, inplace=True)

    # Add neighborhood metrics for each parcel 
    model_predictions = trained_model_df[['prediction']].join(parcel_info)
    model_predictions['model_group'] = model_group
    model_predictions['subset'] = 'All Parcels'
    all_top_k[model_group] = model_predictions.head(k)

    # Get feature importances (or coefficients for Logistic Regression)
    if model_name == 'LogisticRegression':
        feature_importances = pd.DataFrame(data=[trained_model_df.columns[:-1],
                                                 trained_model_dict['model'].coef_[0]]).T

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
    below_median_ID['model_group'] = model_group
    below_median_ID['subset'] = 'Below Insp. Density Median'
    all_top_k[model_group + ' Below Median ID'] = below_median_ID

    # Get list of top k parcels below first quartile ID
    inspection_density_first_quartile = model_predictions.inspection_density.quantile(0.25)
    first_quartile_mask = model_predictions.inspection_density < inspection_density_first_quartile
    below_quartile_ID = model_predictions[first_quartile_mask].head(k)
    below_quartile_ID['model_group'] = model_group
    below_quartile_ID['subset'] = 'Below Insp. Density First Quartile'
    all_top_k[model_group + ' Below First Quartile ID'] = below_quartile_ID
    
all_top = pd.concat(all_top_k.values())
all_top.to_csv(path_to_all_top_k)

all_features_csv = pd.concat(all_feature_importances.values())
all_features_csv.set_index(['feature','model_group']).\
          to_csv(path_to_feature_importances)
