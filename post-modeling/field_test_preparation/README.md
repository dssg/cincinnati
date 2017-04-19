# Preparing Results for a Field Test - Retraining Models & Generating Lists
First, you should have chosen a handful of models to retrain (see model exploration 
section).

Based on the results of the [model exploration step](../model_exploration/), 
we did some hands-on analysis (primarily using Tableau) to select 5 models 
that did the best with respect to precision (finding the 
most violations), 5 models that identified parcels in neighborhoods that had a low
inspection density, 5 models that identified parcels that had a low
neighborhood violation rate, and 5 models that seemed to balance these three 
aspects fairly well. Update the CSV here ([`top_model_reason_lookup.csv`](top_model_reason_lookup.csv)) 
with the group numbers of these models and their respective reasons for selection
before running the following steps.

## Retrain Models & Make a List
Once you've chosen your final model(s), you'll want to retrain them using 
the most recent data available (in our case, the most recent data update was August 31,
2016). The [`retrain_models.py`](retrain_models.py) script does this, creating
a list of the top *k* parcels for each model, as well as a list of the 
model-specific feature importances.

To create a list of parcels to inspect, we use [`generate_list.py`](generate_list.py). 
Given a model group number, this will generate a list of parcels to inspect, 
along with address, latitude, longitude, and number of inspections and violations in 
the neighborhood of that parcel.

Once you have chosen a model and which list subset you want (options: `'All Parcels'`, 
`'Below Insp. Density First Quartile'`, or `'Below Insp. Density Median'`), run
`generate_list.py` to create a list (`inspection_list.csv`). Example: 
> `python generate_list.py '23049' 'All Parcels'` 

## Feature Crosstabs: **_Which types of parcels are ranked highly by each model?_**
We'd like to analyze how the models are making decisions, but sometimes 
interpreting ML models isn't totally straightforward, and sometimes it's 
hard to know if you're comparing "apples to apples." One way we can analyze models
and interpret the mechanisms by which they make decisions is by characterizing the 
"riskiest" parcels a given model identifies and comparing how the data we have about
these risky parcels differs from what we know about the general population of parcels. We do
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
