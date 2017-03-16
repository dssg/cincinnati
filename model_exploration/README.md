# Model Selection & Exploration
**_So I've trained a bunch of models ... now what?_**
Once you've run some experiments and have results from said models, you'll 
want to narrow down the field so that you can have a deeper look and analyze 
your results. The [model selection and exploration](model-selection-and-exploration.ipynb) 
notebook contains the code to do this.

Input: Directory housing your experiments, `space_delta` and `time_delta` 
(specifying the level of space & time you want to cover in the neighborhood
history), and `k` (what level to calculate precision, or how many parcels
will be included in the list of inspections).

Output: `model-results-grouped.csv`, a file with all of the models and their
results on a variety of training and testing windows. A model is defined by
the model type (e.g. Logistic Regression, Random Forest), the parameters used
for that model, and the features and their respective aggregations used (e.g. 
Census up to 400m). 

Based on these model results, we did some hands-on analysis (using Tableau)
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

- Input: `model_groups`
- Output: `all_top5.csv` (a CSV of all the models along with the list of 
their top-ranked 7500 parcels, with model scores and pertinent neighborhood
information for all of those parcels), feature importances (from the models),
feature crosstabs (comparing the top 5% of parcels to the whole population of
parcels), and a heatmap of list overlap.


## Feature Crosstabs
**_What types of parcels are ranked highly by a given model?_**
Sometimes it's not straightforward to interpret models. One thing we can do is
characterize the "riskiest" parcels identified by a model by looking at how 
what we know about them differs from what we know about the general population
of parcels. 

## List Overlap Between Models
**_Does it really matter which model I choose?_**
It's possible that you'd end up with the same list of parcels to inspect, 
regardless of the model. To investigate this, we look at the *overlap* between
the top *k* parcels chosen by each model up for consideration.
  