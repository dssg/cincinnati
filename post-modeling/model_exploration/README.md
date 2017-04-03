# Model Selection & Exploration
**_So I've trained a bunch of models ... now what?_**
Once you've run some experiments and have some preliminary results, you'll 
want to narrow down the field so that you can look more closely and analyze 
your results. 

The [`get_model_groups.py`](get_model_groups.py) script does calculates a 
variety of model performance metrics and measures of inspection and violation 
density for each of the model's training and testing
windows. One model is defined by the model type (e.g. Logistic Regression,
Random Forest), the hyperparameters used, the feature sets included, and the
various levels of spatial and temporal feature aggregations used.   

Specify the directory location of your experiment config files, `space_delta` and 
`time_delta` (specifying the level of space & time you want to cover in the neighborhood
history metrics), `k` (the level at which to calculate precision, or how many parcels
will be included in the list of inspections), and `validation_feature_schema` (used to
get neighborhood information for all parcels).

Based on these results, we did some hands-on analysis (primarily using Tableau)
to choose 5 models that did the best with respect to precision (finding the 
most violations), 5 models that identified parcels in neighborhoods that had a low
inspection density, 5 models that identified parcels that had a low
neighborhood violation rate, and 5 models that seemed to balance these three 
aspects fairly well. We store them in a CSV along with their respective reasons
for selections for the following steps: [`top_model_reason_lookup.csv`](top_model_reason_lookup.csv).

# Retraining Models & Providing Lists

## Retrain Models
Once you've chosen your final model(s), you'll want to retrain them using 
the most recent data available (in our case, the most recent data update was August 31,
2016). The [`retrain_models.py`](retrain_models.py) script does this, creating
`all_top5.csv` (a CSV with a list of the 7500 top-ranked parcels for each model, 
model scores and pertinent neighborhood information for all parcels), as well as a CSV of the 
feature importances for all features used by all models (`feature_importances.csv`).

## Feature Crosstabs
**_Which types of parcels are ranked highly by each model?_**
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

## List Overlap Between Models
**_Does it really matter which model I choose?_**
It's possible that you'd end up with the same list of parcels to inspect, 
regardless of the model. To investigate this, we look at the *overlap* between
the top *k* parcels chosen by each model up for consideration.
To make this figure, run the [`make_list_overlap_heatmap.py`](make_list_overlap_heatmap.py)
script.
 

# Running the Code 
1. Start virtualenv, install requirements:
```
virtualenv cinci-venv
source cinci-venv/bin/activate
pip install -r requirements.txt
```
2. Adapt `../../env_sample.sh` as appropriate
3. `source ../../env.sh` 

