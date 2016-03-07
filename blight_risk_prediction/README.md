# Blight Risk Prediction

###Configure the model to train

Before training a model, edit the `default.yaml` configuration file to select which model to train and features to include. Documentation is on the file.

##Running `model.py`

For detailed information on available options, run:

`./blight_risk_prediction/model.py --help`

Features are loaded from the `features` schema in the database.

###Logging model results

Each time you run a model, the pipeline will store the results. There are different things you can save (training set, model parameters, etc.), some are sent to a MongoDB database and others to your `$OUTPUT_FOLDER`.

[mongolab](https://mongolab.com) provides a free MongoDB database that you can use, make sure you provide a valid mongo URI in the config.yaml file.