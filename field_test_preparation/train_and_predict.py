"""
Given a model_id that has performed well historically, train a model with 
this model_id's configuration and parameters, but using all data up to a 
given train_end date. Then, use this model to predict the outcome for all
datapoints in a given prediction_schema. Return the trained model and the
predictions.
"""
