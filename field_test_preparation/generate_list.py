from sklearn_evaluation.Logger import Logger
from lib_cinci.config import main
from lib_cinci.predict_on_schema import predict_on_schema

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

# step 1 - load model

# load information for the best model
logger = Logger(host=main['logger']['uri'],
                db=main['logger']['db'],
                collection=main['logger']['collection'])
model = logger.get_best_from_experiment(exp_name, metric)

# step 2 - rank all parcels in cincinnati

# use model to predict on every parcel in a given list
preds = predict_on_schema(str(model['_id']), schema)
total = preds.shape[0]
# sort by score
preds.sort_values(by='prediction', inplace=True, ascending=False)

# step 3 -filter
# filter by parcel type? (or maybe group them)
# filter by number of inspections since X
# filter using neighborhood score?


# step 4 - take the top predictions
top_k = int(total*(4/100.0))
subset = preds.head(top_k)

# step 5 - random samplong from the top predictions
inspections_list = subset.sample(n_inspections)
