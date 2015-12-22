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

#2013 census data
#ftp://ftp2.census.gov/geo/pvs/tiger2010st/39_Ohio/39/
#file definitions: http://www2.census.gov/geo/tiger/TIGER2012/2012_TIGERLine_Shapefiles_File_Name_Definitions.pdf

#BLOCK GROUPS
#0. Get the files
wget "ftp://ftp2.census.gov/geo/pvs/tiger2010st/39_Ohio/39/tl_2010_39_bg10.zip" --directory-prefix=$TMP_FOLDER
unzip "$TMP_FOLDER/tl_2010_39_bg10.zip"
#1. Convert to pgsql, SRID is 4269, convert to 3735
shp2pgsql -s 4269:3735 "$TMP_FOLDER/tl_2010_39_bg10.shp" shape_files.census_blocks_groups > "$TMP_FOLDER/census_blocks_groups.sql"
#2. Drop table if exists
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS shape_files.census_blocks_groups;"  
#3. Upload to the database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/census_blocks_groups.sql"

#BLOCKS

#TRACTS
wget "ftp://ftp2.census.gov/geo/pvs/tiger2010st/39_Ohio/39/tl_2010_39_tract10.zip" --directory-prefix=$TMP_FOLDER
unzip "$TMP_FOLDER/tl_2010_39_tract10.zip"
shp2pgsql -s 4269:3735 "$TMP_FOLDER/tl_2010_39_tract10.shp" shape_files.census_tracts > "$TMP_FOLDER/census_tracts.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS shape_files.census_tracts;"  
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/census_tracts.sql"


#Download census data - creates table shape_files.census_pop_housing
python "$CODE_FOLDER/census_api_util_download.py"

#Create features
python "$CODE_FOLDER/census_features.py"