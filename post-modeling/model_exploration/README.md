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

Based on these results, we did some hands-on analysis (primarily using Tableau)
to choose 5 models that did the best with respect to precision (finding the 
most violations), 5 models that identified parcels in neighborhoods that had a low
inspection density, 5 models that identified parcels that had a low
neighborhood violation rate, and 5 models that seemed to balance these three 
aspects fairly well. We store the model group numbers with their respective 
reasons for selection in a table ([`top_model_reason_lookup.csv`](top_model_reason_lookup.csv))
to be used for the following steps.

# Retraining Models & Providing Lists

## Retrain Models & Make a List
Once you've chosen your final model(s), you'll want to retrain them using 
the most recent data available (in our case, the most recent data update was August 31,
2016). The [`retrain_models.py`](retrain_models.py) script does this, creating
`all_top5.csv` (a CSV with a list of the top `k` parcels for each model, 
model scores and pertinent neighborhood information for all parcels), as well as a CSV of the 
feature importances for all features used by all models (`feature_importances.csv`).

To create a list of parcels to inspect, use [`get_inspection_list.py`](get_inspection_list.py). 
Given a model group number, this will generate a list of parcels to inspect, 
along with address, latitude, longitude, and number of inspections and violations in 
the neighborhood of that parcel.

## Feature Crosstabs: **_Which types of parcels are ranked highly by each model?_**
We'd like to analyze how the models are making decisions, but sometimes 
interpreting ML models isn't totally straightforward, and sometimes it's 
hard to know if you're comparing "apples to apples." One way we analyze models
and interpret their decision-making mechanisms is by characterizing the 
"riskiest" parcels a model identifies and comparing how the data we have about
them differs from what we know about the general population of parcels. We do
this by gathering all of the information we have (all features) for all 
parcels, taking the average across all parcels, and then comparing that to
the average of those features across the top-ranked parcels for each model.  

To make the feature crosstabs, run the [`make_feature_crosstabs.py`](make_feature_crosstabs.py)
script.

## List Overlap Between Models: **_Does it really matter which model I choose?_**
It's possible that you'd end up with the same list of parcels to inspect, 
regardless of the model. To investigate this, we use [`make_list_overlap_heatmap.py`](make_list_overlap_heatmap.py)
to create a heatmap displaying *overlap* between the top `k` parcels chosen 
by each model. Example [here](list_overlap_heatmap.png).
 

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

## Creating an Inspection List
Once you have chosen a model and which list subset you want (options: `'All Parcels'`, 
`'Below Insp. Density First Quartile'`, or `'Below Insp. Density Median'`), run
`get_inspection_list.py` to create a list (`inspection_list.csv`). 
`python get_inspection_list.py '23049' 'All Parcels'` 
