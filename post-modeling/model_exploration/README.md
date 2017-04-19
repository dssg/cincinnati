# Model Selection & Exploration
Once you've run some experiments and have some preliminary results, you'll 
want to narrow down the field so that you can look more closely and analyze 
your results. 

First, run [`get_all_model_info.py`](get_all_model_info.py), which goes through a folder of experiment
configs (see [`medium_models`](medium_models/) for example configs), and calculates
a variety of performance metrics and measures of inspection and violation density for each model.

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

Based on these results, we did some hands-on analysis (primarily using Tableau)
to choose 5 models that did the best with respect to precision (finding the 
most violations), 5 models that identified parcels in neighborhoods that had a low
inspection density, 5 models that identified parcels that had a low
neighborhood violation rate, and 5 models that seemed to balance these three 
aspects fairly well. We store the model group numbers with their respective 
reasons for selection in a table ([`top_model_reason_lookup.csv`](top_model_reason_lookup.csv))
to be used for the following steps.

# Running the Code 
1. Make a virtualenv and install required packages:
```
virtualenv cinci-venv
source cinci-venv/bin/activate
pip install -r requirements.txt
```
2. Specify environmental variables: (see [project README](../../README.md), 
[env_sample.sh](../../env_sample.sh))
> `source env.sh` 
3. Update [Drakefile](Drakefile) `VALIDATION_SCHEMA`, `SPACE_DELTA`, and `TIME_DELTA`
and then run drake:
> `drake` 