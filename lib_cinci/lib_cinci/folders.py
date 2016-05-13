import os

output_folder = os.environ['OUTPUT_FOLDER']

# Where to save test set predictions
path_to_predictions = os.path.join(output_folder, "predictions")
# Where to pickle models
path_to_pickled_models = os.path.join(output_folder, "pickled_models")
# Where to pickle scales
path_to_pickled_scalers = os.path.join(output_folder, "pickled_scalers")
# Where to pickle imputers
path_to_pickled_imputers = os.path.join(output_folder, "pickled_imputers")
# Where to dump train and testing sets
path_to_dumps = os.path.join(output_folder, "dumps")
