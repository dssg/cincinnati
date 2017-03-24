# Model Selection & Exploration
**_So I've trained a bunch of models ... now what?_**
Once you've run some experiments and have some preliminary results, you'll 
want to narrow down the field so that you can look more closely and analyze 
your results. The [model exploration and selection](model-exploration-and-selection.py)
script does this.

- **Input**: Directory location of your experiment config files, `space_delta` and 
`time_delta` (specifying the level of space & time you want to cover in the neighborhood
history metrics), `k` (the level at which to calculate precision, or how many parcels
will be included in the list of inspections), `validation_feature_schema` (used to
get neighborhood information for all parcels).

- **Output**: A CSV of models listing their results on various model performance
and neighborhood inspection and violation density on a variety of training and 
testing windows. A model is defined by the model type (e.g. Logistic Regression, 
Random Forest), the hyperparameters used, the features included, and the various
levels of feature aggregations used (e.g. "Census up to 400m"). 

Based on these model results, we did some hands-on analysis (primarily using Tableau)
to choose 5 models that did the best with respect to precision (finding the 
most violations), 5 models that identified parcels in neighborhoods that had a low
inspection density, 5 models that identified parcels that had a low
neighborhood violation rate, and 5 models that seemed to balance these three 
aspects fairly well. 

# Retraining Models & Providing Lists

## Retrain Models
Once you've chosen your final model(s), you'll want to retrain them using all
the most recent data (in our case, the most recent data update was August 31,
2016). The [retrain models](retrain-models.ipynb) notebook does this.

- **Input**: `model_groups` (the model or models found by hand at the end of the step above)
- **Output**: `all_top5.csv` (a CSV with a list of the 7500 top-ranked parcels
for each model, model scores and pertinent neighborhood
information for all parcels), feature importances (from the models),
feature crosstabs (comparing the top 5% of parcels to the whole population of
parcels), and a heatmap of list overlap (similarity between models' top
predictions).

## Feature Crosstabs
**_What types of parcels are ranked highly by a given model?_**
We'd like to analyze how the models are making decisions, but sometimes 
interpreting ML models isn't totally straightforward, and sometimes it's 
hard to know if you're comparing "apples to apples." One way we analyze models
and interpret their decision-making mechanisms is by characterizing the 
"riskiest" parcels a model identifies and comparing how the data we have about
them differs from what we know about the general population of parcels. We do
this by gathering all of the information we have (all features) for all 
parcels, taking the average across all parcels, and then comparing that to
the average of those features across the top-ranked parcels for each model.  

## List Overlap Between Models
**_Does it really matter which model I choose?_**
It's possible that you'd end up with the same list of parcels to inspect, 
regardless of the model. To investigate this, we look at the *overlap* between
the top *k* parcels chosen by each model up for consideration.
 

# Running the Code 
1. Start virtualenv, install requirements:
```
virtualenv --no-site-packages cinci-venv
source cinci-venv/bin/activate
pip install -r requirements.txt
```
2. Adapt `env_sample.sh` as appropriate
3. `source env.sh` 
4. Adapt `model-exploration-and-selection.py` as necessary and then run:
`python model-exploration-and-selection.py`