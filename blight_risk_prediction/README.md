# Blight Risk Prediction

This module contains code for creating features and training a model to predict the probability that a home will have a
building code violation if inspected at some specific date. 

# Run the model

... see Readme file in parent directory

# Create features from raw data

## Create features for each actual inspection in the data

* manually create schema `features` in the database
* open `features/featurebot.py`. In the main function call
     
   
     
    generate_features()
    
* run 

 
    python -m blight_risk_prediction/features/featurebot.py

## Create features as if inspection where on some date, e.g. July 1st 2015

* manually create schema `features_01Jul2015` in the database
* open `features/featurebot.py`. In the main function call
     
   
     
    d = datetime.datetime.strptime("01Jul2015", '%d%b%Y')
    generate_features_for_fake_inspection(d)
    
* run 

 
    python -m blight_risk_prediction/features/featurebot.py

# Adding a new feature

Add features for `featurebot.py`:

*  Define a new feature to generate in `featurebot.features_to_generate()`. This function will generate a new table in 
    the database by pairs of inspection and date, for a list of parcels.
*  Add feature generation code in a separate file `<feature_name>.py`
*  Add feature to the list of features to load when creating training and testing in `dataset.feature_loaders()`
   --> list all columns in feature table!
*  Add a function to load feature in class `FeatureLoader().def load_<feature_name>_feature()`
*  Add a string corresponding to the feature in the default YAML configuration file: list all column names!
*  Start `featurebot` to populate the database with features.
