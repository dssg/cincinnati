#!/usr/bin/env bash
BULK_GEOCODER_FOLDER="$ROOT_FOLDER/bulk_geocoder"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$BULK_GEOCODER_FOLDER/update_distances.sql"