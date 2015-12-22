#!/usr/bin/env bash
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/census"
TMP_FOLDER="$LOCAL_DATA_FOLDER/tmp"
CODE_FOLDER="$ROOT_FOLDER/etl/census"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#mkdir if not exists
mkdir -p $TMP_FOLDER

#Download census data - creates table shape_files.census_pop_housing
python "$CODE_FOLDER/census_api_util_download.py"

#Create features
python "$CODE_FOLDER/census_features.py"