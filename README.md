# Cincinnati Blight

This is the continuation of the Cincinnati [summer project](https://github.com/dssg/cincinnati2015-public) done during DSSG 2015.

## About

First settled in 1788, Cincinnati is one of the oldest American cities west of the original colonies. Today, the 
city struggles with aging home stock, stifling economic redevelopment in some neighborhoods. 

DSSG is working with the City of Cincinnati to identify properties at risk of code violations or abandonment. We hope
that early intervention strategies can prevent further damage and stimulate neighborhood revitalization. Read more about
our project [here](http://dssg.uchicago.edu/2015/08/20/cincy-blight-prevention.html). 

## Setup

### Clone the repo

Clone the repo in `$ROOT_FOLDER`

```bash
git clone https://github.com/dssg/cincinnati $ROOT_FOLDER
```

### Select folders for code, data, and output

The code relies on four bash environment variables (`ROOT_FOLDER`, `DATA_FOLDER`, and `OUTPUT_FOLDER`, and `PYTHONPATH`), which define where this repo, your raw data, and your outputs live. There is an example file,`env_sample.sh`, which looks like this:

```bash
#Where to store the code
export ROOT_FOLDER="/path/to/repo/"
#Where data is stored
export DATA_FOLDER="/path/to/data/"
#Where to output results from models
export OUTPUT_FOLDER="/path/to/output/"

#Add lib folder to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$ROOT_FOLDER/lib_cinci
```

Modify the three environment variables as appropriate. The `PYTHONPATH` line 
is also necessary since it includes many functions used across the project. 
Consider adding that to your shell profile, so they get loaded automatically, or `source` the file before running the pipeline.

### Provide `config.yaml`, `logger_config.yaml` and `.pgpass`

The code loads some parameters from a `config.yaml` file stored in the `$ROOT_FOLDER`. This file lists your connection parameters to a Postgres DB and a Mongo DB, which will be used in throughout the pipeline. Use the `config_sample.yaml` file to see the structure and then rename it to `config.yaml`. Make sure that the file is stored in your `$ROOT_FOLDER`. 

`logger_config.yaml` configures the logger for the Python interpreter. Customize it as you please; it is git-ignored.

For parts of the ETL, you will also need a `.pgpass` file (note the dot). This file needs to be saved as `$ROOT_FOLDER/.pgpass` to build it. If you are not going to use Docker, just make sure that a standard `.pgpass` file is on your home folder. See `.pgpass_sample` for syntax details. This file gives the connection parameters for your Postgres DB.

### Resources

This project relies on a data dump from the City of Cincinnati. Some of the data is publicly available, and pulled from the city's open data API. Some data is private, and was delivered by the City of Cincinnati. More details on the data layout can be found in the [pre-modeling folder](pre-modeling/etl).

The pipeline makes use of a Postgres DB, used for storing the raw data and generated features. Some of the feature generation (especially aggregations over spatial features) are computationally expensive (and not optimized), and might take a medium-sized Postgres server several days to complete. The pipeline also requires a (small) Mongo DB, which is used a logger for model outputs. Here, we used [MLab](https://mlab.com/) for convenience.

The pipeline conducts a naive gridsearch over several hyperparameters, replicated across several temporal splits for temporal cross-validation. The model fitting happens in Python (using [scikit-learn](http://scikit-learn.org/stable/). We ran the model fitting on several large AWS machines, broken up by temporal ranges.

## Overall Data Pipeline

Once you have set up your environment, you can start using the pipeline, the general procedure is the following (specific instructions for each step are available inside each subfolder):

1. Load data into the database 
   1. Use the [pre-modeling folder](pre-modeling/) to upload all the data to the database
   2. Perform geocoding on some datasets. Use the [bulk_geocoder](pre-modeling/bulk_geocoder/) for this.
2. [Generate features](model/features) from the data
4. Run some experiments. Use `model.py` inside [model](model/) to train models. `model.py` requires you to provide a configuration file, see `default.yaml` in this folder for reference.  [experiments](model/experiments) folder contains more examples.
5. Evaluate model performance and generate lists for field tests using the
[post-modeling](post-modeling/) directory.
