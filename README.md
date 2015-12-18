This is the continuation of the Cincinnati [summer project](https://github.com/dssg/cincinnati2015) done during DSSG 2015.

## About

First settled in 1788, Cincinnati is one of the oldest American cities west of the original colonies. Today, the 
city struggles with aging home stock, stifling economic redevelopment in some neighborhoods. 

DSSG is working with the City of Cincinnati to identify properties at risk of code violations or abandonment. We hope
that early intervention strategies can prevent further damage and stimulate neighborhood revitalization. Read more about
our project [here](http://dssg.uchicago.edu/2015/08/20/cincy-blight-prevention.html). 

##Select one folder for the data and another for the code

##Clone the repo

##Put the data following the repo structure

##Provide config.yaml and .pgpass

##Build docker ETL image

`docker build -t cincinnati .`

##Run docker image

`docker run -v ~/data/cincinnati-data:/root/data -v /Users/Edu/Development/dsapp/cincinnati-dsapp:/root/code -i -t cincinnati /bin/bash`

##Run the ETL pipeline

##Create features from the data

... see the blight_risk_prediction directory

## Run the modeling pipeline

##Create output directories

    mkdir results
    mkdir predictions
    
##Configure the model

    edit default.yaml (options are documented in default.yaml)
    
##Run the model

    python -m blight_risk_prediction/model
   
#### Output

Each model run produces a pickle file which contains:

* the full list of parcels predicted to have violations
* the configuration file used to generate that model
* feature importances

These output files include a timestamp in their filename such that they will not be accidentally overwritten. These files can be used with the evaluation web application in `evaluation`. 

## Repository layout

* blight_risk_prediction - our modeling pipeline
* docs - some additional documentation
* etl - scripts for loading the Cincinnati datasets into a postgres database
* evaluation - webapp we use for comparing different models
* postprocess - add details (e.g. address) about properties to predictions
* targeting_priority - re-rank predictions according to some targeting priority
* test - unit tests

