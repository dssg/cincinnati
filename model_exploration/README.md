# Model Selection & Exploration
**_So I've trained a bunch of models ... now what?_**
Once you've run some experiments and have some preliminary results, you'll 
want to narrow down the field so that you can look more closely and analyze 
your results. The [model selection and exploration](model-selection-and-exploration.ipynb) 
notebook contains the code to do this.

- **Input**: Directory housing your experiments, `space_delta` and `time_delta` 
(specifying the level of space & time you want to cover in the neighborhood
history), and `k` (the level at which to calculate precision, or how many parcels
will be included in the list of inspections).

- **Output**: `model-results-grouped.csv`, a file with all of the models and their
results on a variety of training and testing windows. A model is defined by
the model type (e.g. Logistic Regression, Random Forest), the parameters used
for that model, and the features and their respective aggregations used (e.g. 
Census up to 400m). 

Based on these model results, we did some hands-on analysis (primarily using Tableau)
to choose 5 models that did the best with respect to precision (finding the 
most violations), 5 models that identified inspections that had a lower
inspection density, 5 models that identified parcels to inspect with a lower
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
  