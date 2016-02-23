#Feature generation [WORK IN PROGRESS]

##Generating features

Once you have uploaded all the data, you will be able to generate features for the model, for more information run:

`./blight_risk_prediction/features/featurebot.py --help`

##About feature schemas

[WIP]

##Generating features for arbitrary inspections list

When training models, we select a training size and a validation window, this gives us a way to calculate metrics for our models and rank them according to our precision ad 1% metric.

However, we want to also be able to predict on other sets than the one we get from the validation window:

1. Predict on inspections from field tests. We currently have a list of 100+ new inspections conducted as a result of the summer project, this list can also serve as a testing set for our models
2. Predict on all parcels for a given data. When preparing a new inspection list for our partner, we want to generate features for all parcels in Cincinnati

Note: Currently, predicting on all parcels is done in `model.py`, but it will be better to integrate it here so `model.py` is simpler and does only one job.

##Adding new features

Add features for `featurebot.py`:

*  Define a new feature to generate in `featurebot.features_to_generate()`. This function will generate a new table in 
    the database by pairs of inspection and date, for a list of parcels.
*  Add feature generation code in a separate file `<feature_name>.py`
*  Add feature to the list of features to load when creating training and testing in `dataset.feature_loaders()`
*  Start `featurebot` to populate the database with features.