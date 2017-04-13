# Feature generation

This folder contains several functions that calculate various features, all following the same convention. To generate features, you'll interface with the `featurebot.py` script.

## Generating features

Once you have uploaded all the data, you will be able to generate features for the model, for more information run:

`./model/features/featurebot.py --help`

In short, `featurebot.py` takes three main arguments: The name of the feature you wish to generate, the spatial radius over which that feature should aggregate (if the feature is spatial), the temporal window over which the feature should aggregate, and the as-of date, i.e., the last day for which the feature should use data.

This pipeline makes an important design decision regarding the as-of ('`fake_today`') dates: When you choose an as-of date, then the pipeline calculates the given feature, using available data up to that as-of date, *for each parcel in the city*. Generally, inspections in the pipeline are identified by the tuple consisting of (`parcel_id`, `inspection_date`). Thus, when generating features up to a given as-of date, the pipeline pretends that there is an inspection (`parcel_id`, `<as_of_date>`) for every possible `parcel_id`. However, when *no* date is given to `featurebot.py`, then the pipeline calculates features only for inspections that *actually happened*, using the `inspection_date` as the as-of date. In other words, when passing no date to `featurebot.py`, then the pipeline calculates features for each (`parcel_id`, `inspection_date`), where the spatial aggregations are performed for the chosen radius around `parcel_id`'s location, and the temporal aggregations are performed going backward in time from `inspection_date`. Thus, in a sense, every inspection carries its own as-of date. (This is a design decision that we do not generally recommend.)

## Inspecting the Postgres DB after Feature Generation

After feature generation, you will find several new schemas in the Postgres DB. The `features` schema contains the features that were calculated for inspections that actually happened, the as-of date always set to the inspection's `inspection_date`. The number of rows in this schema's tables will be identical to the number of inspections in your dataset. The `parcels_inspections` table in this schema contains all inspections from our partner's database, thus features are generated for every *real* inspection. This schema is used for training models.

There will also be schemas with names following the pattern of `features_31dec2015`. One such schema should exist for each date that you passed to `featurebot.py`. These schemas contain the features that were calculated using data up to the specific date (the '`fake_today`'). Note that each table in each of these schemas will have one row *for each `parcel_id` in Cincinnati*. The `inspection_date` will be set to the as-of date for all these parcels. These schemas are used to generate predictions from a trained model.

## Adding new features

Add features for `featurebot.py`:

*  Define a new feature to generate in `featurebot.features_to_generate()`. 
*  Add feature generation code in a separate file `<feature_name>.py`
*  Start `featurebot` to populate the database with features.

## Note on feature loading

After features are created, you can start training models. `dataset.py` handles the loading logic. When specifying features for training in the configuration file, you are actually selecting tables and columns, the pipeline groups together columns in the same table so they get loaded in a single call to the database. The summer pipeline required you to add a custom loading method for every table, which is good for security reasons but bad for flexibility. Right now, the pipeline uses a function that returns another function to load any group of columns (see `generate_loader_for_table` function in `dataset.py`), but the function is incomplete and will only work for tables that have a `parcel_id and `inspection_date` column.
