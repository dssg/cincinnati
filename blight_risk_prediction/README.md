# Blight Risk Prediction

This module contains code for creating features and training a model to predict the probability that a home will have a
building code violation if inspected at some specific date. 

##Adding new features

Add features for `featurebot.py`:

*  Define a new feature to generate in `featurebot.features_to_generate()`. This function will generate a new table in 
    the database by pairs of inspection and date, for a list of parcels.
*  Add feature generation code in a separate file `<feature_name>.py`
*  Add feature to the list of features to load when creating training and testing in `dataset.feature_loaders()`
*  Start `featurebot` to populate the database with features.