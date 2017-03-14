# Feature generation

## Generating features

Once you have uploaded all the data, you will be able to generate features for the model, for more information run:

`./model/features/featurebot.py --help`

## Generating features for arbitrary inspections list

When training models, we select a training size and a validation window, this gives us a way to calculate metrics for our models and rank them according to our precision ad 1% metric.

However, we want to also be able to predict on other sets than the one we get from the validation window:

1. Predict on inspections from field tests. We currently have a list of 100+ new inspections conducted as a result of the summer project, this list can also serve as a testing set for our models
2. Predict on all parcels for a given data. When preparing a new inspection list for our partner, we want to generate features for all parcels in Cincinnati

For doing that, we organized features on different database schemas, which are explained below.

## About feature schemas

Features are stored in different database schemas to ease data manipulation. Every schema storing features needs to have a `parcels_inspections` table, and features are generated for those inspections only. There are four types of schemas:

* General schema (`features`): the `parcels_inspections` table in this schema contains all inspections from our partner's database, thus features are generated for every *real* inspection. This schema is used for training models.
* General schema with fake date (`features_DATE`): the `parcels_inspections` table in this schema also contains all inspections from our partner's database, but the inspection date is changed to `DATE`. This schema is used to generate predictions from a trained model.
* Field test inspections (`features_field_test`): this schema includes inspections that happened after the summer project ended, the objective is to use this as an alternative test set for our models, given that those inspections happened in Ausgust 2015 (and we don't have all the data for generating for that year), we need to fake the inspection date, and that's the purpose of the last schema.
* Field test insepctions with fake date (`features_field_test_DATE`): this schema uses the list of inspections that happened during the summer and changes the date for something that we can use for generating features, this schema can be used as an alternative test set for our models.

## Adding new features

Add features for `featurebot.py`:

*  Define a new feature to generate in `featurebot.features_to_generate()`. 
*  Add feature generation code in a separate file `<feature_name>.py`
*  Start `featurebot` to populate the database with features.


## Note on feature loading

After features are created, you can start training models. `dataset.py` handles the loading logic. When specifying features for training in the configuration file, you are actually selecting tables and columns, the pipeline groups together columns in the same table so they get loaded in a single call to the database. The summer pipeline required you to add a custom loading method for every table, which is good for security reasons but bad for flexibility. Right now, the pipeline uses a function that returns another function to load any group of columns (see `generate_loader_for_table` function in `dataset.py`), but the function is incomplete and will only work for tables that have a `parcel_id and `inspection_date` column.
