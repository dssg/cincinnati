import os

#Where to save test set predictions
path_to_predictions = os.path.join(os.environ['OUTPUT_FOLDER'], "predictions")
#Where to pickle models
path_to_pickled_models = os.path.join(os.environ['OUTPUT_FOLDER'], "pickled_models")
#Where to pickle scales
path_to_pickled_scalers = os.path.join(os.environ['OUTPUT_FOLDER'], "pickled_scalers")
#Where to pickle imputers
path_to_pickled_imputers = os.path.join(os.environ['OUTPUT_FOLDER'], "pickled_imputers")
#Where to dump train and testing sets
path_to_dumps = os.path.join(os.environ['OUTPUT_FOLDER'], "dumps")
