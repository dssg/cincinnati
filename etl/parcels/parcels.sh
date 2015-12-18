#!/usr/bin/env bash
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/parcels"
TMP_FOLDER="$LOCAL_DATA_FOLDER/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#mkdir if not exists
mkdir -p $TMP_FOLDER

#Upload gdb to postgres in shape_files schema
#http://gis.stackexchange.com/questions/83016/how-to-import-esri-geodatabase-format-gdb-into-postgis
#http://www.gdal.org/ogr2ogr.html
ogr2ogr -f "PostgreSQL" PG:"host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER active_schema=shape_files" "$LOCAL_DATA_FOLDER/HamcoParcelData.gdb" -overwrite -progress --config PG_USE_COPY YES


#Convert shapefiles to SQL and upload them to the database
#This one is throwing and error
#shp2pgsql  "/mnt/data3/cincinnati/summer-data/Geodata/ParcPolyWithBldinfo/Parcelpoly_with_Bldinfo_Full.shp" > "$TMP_FOLDER/parcels_w_building_info_full.sql"

shp2pgsql  "$LOCAL_DATA_FOLDER/Parcpoly_with_Bldinfo.shp" shape_files.parcels_w_building_info > "$TMP_FOLDER/parcels_w_building_info.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/parcels_w_building_info.sql"

echo "Done uploading parcels data to postgres"