# Model Selection & Exploration: **_So I've trained a bunch of models ... now what?_**
Once you've run some experiments and have some preliminary results, you'll 
want to narrow down the field so that you can look more closely and analyze 
your results. 

First, run [`get_all_model_info.py`](get_all_model_info.py), which goes through a folder of experiment
configs (see [`medium_models`](medium_models/) for example configs), and calculates
a variety of performance metrics and measures of inspection and violation density for each model.

You will need to specify the directory location of your experiment config files, `space_delta` 
and `time_delta` (specifying the level of space & time you want to cover in the neighborhood
history metrics), `k` (the level at which to calculate precision, or how many parcels
will be inspected), and `validation_feature_schema` (used to get neighborhood history
for each parcel).

This script calculates each model's precision on the validation window (the 6 months 
immediately following the model's testing window). It also calculates the mean and 
standard deviation of the inspection density (inspections per house) and violation 
rate (violations per inspection) in the top `k` parcels selected by each model
(in the `space_delta` meters surrounding the parcel, over the past `time_delta` months),
as well as the percent of parcels in the top `k` which have inspection densities
or violation rates below the first quartile (i.e. in the bottom 25%) of all parcels
in Cincinnati.

[`get_model_groups.py`](get_model_groups.py) groups together models with the same 
feature sets and hyperparameters over different training and testing dates, so
that you can evaluate the performance of models trained with a given combination of 
features and parameters over time.

 
# Running the Code 
1. Start virtualenv, install requirements:
```
virtualenv cinci-venv
source cinci-venv/bin/activate
pip install -r requirements.txt
```
2. Adapt `../../env_sample.sh` as appropriate
3. `source ../../env.sh` 
4. `drake` 

