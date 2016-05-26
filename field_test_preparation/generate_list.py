from datetime import datetime

from sklearn_evaluation.Logger import Logger
import pandas as pd
from sqlalchemy import create_engine

from lib_cinci.config import main
from lib_cinci.predict_on_schema import predict_on_schema
from lib_cinci.evaluation import add_inspections_results_for
from lib_cinci.db import uri

# generate a list of inspections based on a model predictions

# parameters

# experiment name
exp_name = 'exp4_spr16_jan13_may15_only_400m'
# metric to select the best trial for a given experiment
metric = 'prec_at_5'
# db schema used to get the features from
schema = 'features_01may2015'
# top_percent - percent taken from the top
# used for random sampling
percent = 4
# n_inspections - list length
n_inspections = 1000
# nei_schema - db schema used to look for the neighborhood score
# table
nei_schema = 'features_01may2015'
# nei_table - db table used to get the neighborhood scores from
nei_table = 'neighborhood_score_500m_6months'

# step 1 - load model

# load information for the best model
logger = Logger(host=main['logger']['uri'],
                db=main['logger']['db'],
                collection=main['logger']['collection'])
model = logger.get_best_from_experiment(exp_name, metric)

# training window
train_start = datetime.strptime(model['config']['start_date'], '%d%b%Y')
train_end = datetime.strptime(model['config']['fake_today'], '%d%b%Y')
# change the format to match the one needed for the db
train_start = train_start.strftime('%Y-%m-%d')
train_end = train_end.strftime('%Y-%m-%d')
today = datetime.utcnow().strftime('%Y-%m-%d')

# step 2 - rank all parcels in cincinnati

# use model to predict on every parcel in a given list
preds = predict_on_schema(str(model['_id']), schema)

# drop inspection date column and viol_outcime, we don't need it
preds.reset_index(inplace=True)
preds.drop('inspection_date', axis=1, inplace=True)
preds.drop('viol_outcome', axis=1, inplace=True)
preds.set_index('parcel_id', inplace=True)
# add rank column
preds['score_rank'] = preds.prediction.rank(method='min', ascending=False)

total = preds.shape[0]
# sort by score
preds.sort_values(by='prediction', inplace=True, ascending=False)

# step 3 - add extra information
# add inspection results from the last date
# used for traininig until now
preds = add_inspections_results_for(preds, train_end, today)

# add type of parcel

# add neighborhood score
engine = create_engine(uri)
nei_score = pd.read_sql_table(nei_table, engine, schema,
                              index_col=['parcel_id', 'inspection_date'])
nei_score['metric'] = (nei_score.unique_violations / nei_score.houses)
nei_score['insp_density'] = (nei_score.unique_inspections / nei_score.houses)
nei_score.sort_values(by='metric', ascending=False, inplace=True)
# remove unused columns
nei_score.reset_index(inplace=True)
nei_score.drop('inspection_date', axis=1, inplace=True)
nei_score.set_index('parcel_id', inplace=True)
# Filter neighborhood score table...
# since not all cincinnati parcels have been inspected we cannot
# truste the neighborhood score in areas that don't have inspections
insp_density_median = nei_score.insp_density.median()
sub_score = nei_score[nei_score.insp_density >= insp_density_median]
preds = preds.join(nei_score[['metric']])

# step 4 - filter
# filter by parcel type? (or maybe group them)
# filter by number of inspections since X
# filter using neighborhood score?


# step 5 - take the top predictions
top_k = int(total*(4/100.0))
subset = preds.head(top_k)

subset[subset.inspections.notnull()]

# step 6 - random samplong from the top predictions
inspections_list = subset.sample(n_inspections)
