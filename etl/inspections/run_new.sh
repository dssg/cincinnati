#!/usr/bin/env bash
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/inspections"
LOCAL_CODE_FOLDER="$ROOT_FOLDER/etl/inspections"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)


#Step 1: Export Oracle dump to SQL

#Step 2: Upload data


#Step 3: Create view