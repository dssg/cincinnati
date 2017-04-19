# Model Selection & Exploration
Once you've run some experiments and obtained some preliminary results, you'll 
want to narrow down the field of models, analyze their performance, and 
eventually generate an inspection list based on your results.

First, go through all of your trained models, compute metrics, and compare.
Choose a few based on precision, inspection density, violation rate,
and compromise. Do this in the [model_exploration](model_exploration/)
directory.

Next, after you've evaluated and chosen models, you'll want to retrain those
models on the most recent available data and generate a list of parcels
to inspect. The code to do that is in the [field_test_preparation](field_test_preparation/)
directory. 