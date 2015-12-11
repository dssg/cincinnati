This is the continuation of the Cincinnati [summer project](https://github.com/dssg/cincinnati2015) done during DSSG 2015.

## About

First settled in 1788, Cincinnati is one of the oldest American cities west of the original colonies. Today, the 
city struggles with aging home stock, stifling economic redevelopment in some neighborhoods. 

DSSG is working with the City of Cincinnati to identify properties at risk of code violations or abandonment. We hope
that early intervention strategies can prevent further damage and stimulate neighborhood revitalization. Read more about
our project [here](http://dssg.uchicago.edu/2015/08/20/cincy-blight-prevention.html). 

## Getting started

#### Get the code

    git clone https://github.com/dssg/cincinnati.git
    cd cincinnati

##Environmental variables

##Setup data folder

`python -c 'from python_ds_tools import data_folder; data_folder.setup()'`

#install unix dependencies

gdal, gnumeric (for converting xls)

this repo assumes that your default schema is 'public'

--

#### Install all pre-requisites
    conda create -n "cincinnati" --yes --file requirements.conda python=2.7
    source activate cincinnati

#### Configure database
    cp dbconfig.sample dbconfig.py
    update database configuration in dbconfig.py

## Load data into postgres

... see the etl directory

## Create features from the data

... see the blight_risk_prediction directory

## Run the modeling pipeline

#### Create output directories

    mkdir results
    mkdir predictions
    
#### Configure the model

    edit default.yaml (options are documented in default.yaml)
    
#### Run the model

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

