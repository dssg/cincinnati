#Feature generation [WORK IN PROGRESS]

##Generating features

Once you have uploaded all the data, you will be able to generate features for the model, for more information run:

`./blight_risk_prediction/features/featurebot.py --help`

##Adding new features

Add features for `featurebot.py`:

*  Define a new feature to generate in `featurebot.features_to_generate()`. This function will generate a new table in 
    the database by pairs of inspection and date, for a list of parcels.
*  Add feature generation code in a separate file `<feature_name>.py`
*  Add feature to the list of features to load when creating training and testing in `dataset.feature_loaders()`
*  Start `featurebot` to populate the database with features.