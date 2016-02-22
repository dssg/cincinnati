# Blight Risk Prediction

##Adding new features

Add features for `featurebot.py`:

*  Define a new feature to generate in `featurebot.features_to_generate()`. This function will generate a new table in 
    the database by pairs of inspection and date, for a list of parcels.
*  Add feature generation code in a separate file `<feature_name>.py`
*  Add feature to the list of features to load when creating training and testing in `dataset.feature_loaders()`
*  Start `featurebot` to populate the database with features.

###Configure the model to train

Before training a model, efit the `default.yaml` configuration file to select which model to train and features to include. Documentation is on the file.

##Modeling
For information on how to run models, run:

`./blight_risk_prediction/model.py --help`

This module contains code for creating features and training a model to predict the probability that a home will have a
building code violation if inspected at some specific date. 

###Logging model results

Each time you run a model, the pipeline will store the results. There are two ways to do this (to change, modify the `--how_to_save` parameter when running `model.py`:

1. Log to a MongoDB database
2. Pickle results and save them to disk

If you decide to use MongoDB ([mongolab](https://mongolab.com) provides a free instance that you can use), some results will be saved in a collection,
make sure you provide a valid mongo URI in the config.yaml file. However, for performance reasons, predictions will be stored as csv files in `$OUTPUT_FOLDER/predictions`. Make sure that folder exists in your `$OUTPUT_FOLDER`.

If you prefer to pickle results, .pkl files will be stored in `$OUTPUT_FOLDER/pickled_results`. Those files can be visualized using the webapp that the summer team developed.

The recommended way is to use MongoDB, since it's the most complete one.
