# Model Selection & Exploration
## **_So I've trained a bunch of models ... now what?_**
Once you've run some experiments and have some preliminary results, you'll 
want to narrow down the field so that you can look more closely and analyze 
your results. 

First, go through all of your trained models, compute metrics, and compare.
Choose a few based on precision, inspection density, violation rate,
and compromise. Do this in the [model_exploration](model_exploration/)
directory.

Next, after you've evaluated and chosen models, you'll want to retrain those
models on the most recent available data and generate a list of parcels
to inspect. The code to do that is in the [field_test_preparation](field_test_preparation/)
directory. 