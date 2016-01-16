#Cincinnati project

This is the continuation of the Cincinnati [summer project](https://github.com/dssg/cincinnati2015) done during DSSG 2015.

#About

First settled in 1788, Cincinnati is one of the oldest American cities west of the original colonies. Today, the 
city struggles with aging home stock, stifling economic redevelopment in some neighborhoods. 

DSSG is working with the City of Cincinnati to identify properties at risk of code violations or abandonment. We hope
that early intervention strategies can prevent further damage and stimulate neighborhood revitalization. Read more about
our project [here](http://dssg.uchicago.edu/2015/08/20/cincy-blight-prevention.html). 

#Setup

##Select folders for the code, data and output

The code relies on three environment variables, before you start running the code, decide where are you going to store the *raw data*,  *code* and *output*.

Then add these three environment variables:

`export ROOT_FOLDER="/absolute/path/to/the/repo"`

`export DATA_FOLDER="/absolute/path/to/the/raw/data"`

`export OUTPUT_FOLDER="/absolute/path/to/output/folder"`

Consider adding that to your shell profile.

##Clone the repo

Clone the repo in `$ROOT_FOLDER`

`git clone https://github.com/dssg/cincinnati $ROOT_FOLDER`

##Put the data following the repo structure

The pipeline follows certain simple conventions to make the code easy to understand. It is assumed that a file in `$ROOT_FOLDER/etl/something/` will get its raw data from `$DATA_FOLDER/etl/something/`.

Having, said that it's easy to know where to store the raw data. For example, the code that loads all taxes data is `$ROOT_FOLDER/etl/taxes/taxes.sh`, then, your raw taxes files should be stores in `$DATA_FOLDER/etl/taxes/`

The other convention is that intermediate files are stored on a `tmp/` folder, for example, since we need to preprocess the taxes files before uploading them to the database, the intermediate csv files will be on `$DATA_FOLDER/etl/taxes/tmp/`.

##Provide config.yaml and pgpass

The code loads some parameters from a `config.yaml` file stored in the `$ROOT_FOLDER`.

Use the `config_sample.yaml` file to see the structure and then rename it to `config.yaml`, make sure that the file is stored in your `$ROOT_FOLDER`.

`.pgpass` (note the dot) is needed if your are going to use the Docker image and it will take
the file in `$ROOT_FOLDER/.pgpass` to build it. If you are not going to use Docker, just make sure that a standard `.pgpass` file is on your home folder. See `.pgpass_sample` for syntax details.

##Build docker ETL image

The ETL step depends on these programs:

* Python 2.7.11
* GDAL 1.11.2
* Java 1.8
* psql (PostgreSQL) 9.3.10
* PostGIS 2.1.4
* mdbtools 0.7.1 
* gnumeric 1.12.9
* stanford-ner-2015-12-09
* ...and many Python packages

To ease the setup, a Dockerfile is provided which builds an Ubuntu 14.04 image with all dependencies included and properly configured.

Most dependencies are needed for the ETL step, after the raw data is on the database, only Python (and a few packages) and psql is needed, hence, if you want, you can use the Docker image for the ETL phase only. However, the Docker container is the easiest way to run the pipeline and hence, the rest of this instructions assume you are running code inside the container.

For information on how to setup Docker, see the [official docs](https://docs.docker.com/).

Once Docker is properly setup, go to your `$ROOT_FOLDER` and run:

`docker build -t cincinnati .`

This process takes a long time since it needs to download and install all dependencies, but with a decent internet connection is should take less than 1 hour.

##Run docker image

Once the image is ready, run it: 

`docker run -v $DATA_FOLDER:/root/data -v $ROOT_FOLDER:/root/code -v $OUTPUT_FOLDER:/root/output -i -t cincinnati /bin/bash`

Note that we are passing our three environment variables, and linking them to three folders inside the container. The purpose of the Docker container is to run code but not to store anything (not code and of course not data).

We are also forwarding the 4000 from the container to the host, this port is used for the evaluation webapp.

##Setup your database

The data is organized in different schemas, before you start loading any data, run the following script.

`./db_setup.sh`

*Important:* it is assumed that you are using PostgreSQL with PostGIS installed as your database. Make sure that you have [PostGIS](http://postgis.net/) installed before proceeding. This is the only manual step you need to do.

#Data Pipeline

For this part, it is assumed that you are logged in the Docker container inside the `/root/code` folder.

##ETL

Inside the [etl](etl/), you will find one folder for each dataset that we used. For each folder, a shell script (with the same name as the parent folder) is provided which performs the etl for that dataset.

For example, to load the cagis data, run:

`bash etl/cagis/cagis.sh`

##Feature generation

Once you have uploaded all the data, you will be able to generate features for the model, to do that run:

`python -m blight_risk_prediction.features.featurebot`

See [blight_risk_prediction/](blight_risk_prediction/) folder for more details on how to generate features.
 
##Modeling

###Logging model results

Each time you run a model, the pipeline will store the results. There are two ways to do this (to change, modify the `HOW_TO_SAVE` variable in `blight_risk_prediction/model.py`):

1. Log to a MongoDB database
2. Pickle results and save them to disk

If you decide to use MongoDB ([mongolab](https://mongolab.com) provides a free instance that you can use), some results will be saved in a collection,
make sure you provide a valid mongo URI in the config.yaml file. However, for performance reasons, predictions will be stored as csv files in `$OUTPUT_FOLDER/predictions`. Make sure that folder exists in your `$OUTPUT_FOLDER`.

If you prefer to pickle results, .pkl files will be stored in `$OUTPUT_FOLDER/pickled_results`. Those files can be visualized using the webapp that the summer team developed.

###Configure the model to train

Before training a model, efit the `default.yaml` configuration file to select which model to train and features to include. Documentation is on the file.

###Run the model

To run a model using the `default.yaml` configuration file:

    python -m blight_risk_prediction.model

## Repository layout

* blight_risk_prediction - our modeling pipeline
* docs - some additional documentation
* etl - scripts for loading the Cincinnati datasets into a postgres database
* evaluation - webapp we use for comparing different models
* postprocess - add details (e.g. address) about properties to predictions
* targeting_priority - re-rank predictions according to some targeting priority
* test - unit tests

