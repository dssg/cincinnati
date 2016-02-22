#!/usr/bin/env bash
SUMMER_FOLDER="$DATA_FOLDER/etl/summer-test"
TMP_FOLDER="$DATA_FOLDER/etl/summer-test/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#mkdir if not exists
mkdir -p $TMP_FOLDER

#Convert files
ssconvert "$SUMMER_FOLDER/8-21-2015.xls" "$TMP_FOLDER/8-21-2015.csv"
ssconvert "$SUMMER_FOLDER/8-24-2015.xls" "$TMP_FOLDER/8-24-2015.csv"

#Clean and upload to the database
python "$ROOT_FOLDER/etl/summer-test/process.py"