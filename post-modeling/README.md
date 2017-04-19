# Post-Modeling: Model Exploration & Selection and Field Test Preparation
Once you've run some experiments and obtained some preliminary results, you'll 
want to narrow down the field of models, analyze their performance, and 
use the model to choose some parcels to inspect.

First, go through all the models you trained, and choose some of the best-performing
models based on precision, inspection density, violation rate, or some compromise
between the three. The code to do this lives in the [model_exploration](model_exploration/)
directory.

Next, after you've compared models and chosen some candidates, you'll want to 
retrain them on current data, generate a list of inspections to perform, and 
interpet your results. Code to do this lives in the 
[field_test_preparation](field_test_preparation/) directory.
