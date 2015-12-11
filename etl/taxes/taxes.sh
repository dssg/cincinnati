#!/usr/bin/env bash
TAXES_FOLDER="$DATA_FOLDER/etl/taxes"
TMP_FOLDER="$DATA_FOLDER/etl/taxes/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#mkdir if not exists
mkdir -p $TMP_FOLDER

echo "Converting data from $TAXES_FOLDER"

psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2015;"

#Load taxes file and create sql table
python "$ROOT_FOLDER/etl/taxes/Extract2015Taxes.py"