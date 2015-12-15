#!/usr/bin/env bash
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/cagis"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#Upload gdb to postgres in shape_files schema
#http://gis.stackexchange.com/questions/83016/how-to-import-esri-geodatabase-format-gdb-into-postgis
#http://www.gdal.org/ogr2ogr.html
ogr2ogr -f "PostgreSQL" PG:"host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER active_schema=shape_files" "$LOCAL_DATA_FOLDER/CAGIS_Boundaries.gdb" -overwrite -progress --config PG_USE_COPY YES

echo 'Done uploading water cagis data to postgres'