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
#Full documentation: http://www2.census.gov/geo/pdfs/maps-data/data/tiger/tgrshp2010/TGRSHP10SF1.pdf

#Function to download, unzip and upload census to the database (shape_files schema)
#Pass URL to download the file and output name, such name will be used
#for intermediate results (file downloaded, sql scripts) as well as table
#name
function get_census {
    URL=$1
    FILENAME=$2
    OUTPUT=$3
    echo "Downloading file..."
    wget $URL --directory-prefix=$TMP_FOLDER
    echo "Unziping..."
    unzip "$TMP_FOLDER/$FILENAME.zip" -d $TMP_FOLDER
    echo "Converting shp to sql..."
    #Convert from 4269 SRID to 3735 SRID
    shp2pgsql -s 4269:3735 "$TMP_FOLDER/$FILENAME.shp" "shape_files.$OUTPUT" > "$TMP_FOLDER/$OUTPUT.sql"
    echo "Running on db: DROP TABLE IF EXISTS shape_files.$OUTPUT;"  
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS shape_files.$OUTPUT;"  
    echo "Uploading data to the database..."
    psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/$OUTPUT.sql"
    echo "Done! Table $OUTPUT created!"
}

#TRACTS
get_census "ftp://ftp2.census.gov/geo/pvs/tiger2010st/39_Ohio/39/tl_2010_39_tract10.zip" tl_2010_39_tract10 census_tracts

#BLOCK GROUPS
get_census "ftp://ftp2.census.gov/geo/pvs/tiger2010st/39_Ohio/39/tl_2010_39_bg10.zip" tl_2010_39_bg10 census_blocks_groups

#BLOCKS
get_census "ftp://ftp2.census.gov/geo/pvs/tiger2010st/39_Ohio/39/tl_2010_39_tabblock10.zip" tl_2010_39_tabblock10 census_blocks

#Run script with changes to census tables, mostly column renaming
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/process_census_tables.sql"  

#Download census data - creates table shape_files.census_pop_housing
python "$CODE_FOLDER/census_api_util_download.py"

#Map parcels to tracts
#Create shape_files.parcels_cincy table which is a subset of Hamilton parcels
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$CODE_FOLDER/map_parcels_to_tracts_geocode.sql"

#Remove duplicates in shape_files.parcels_cincy
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$CODE_FOLDER/remove_parcels_duplicates.sql"

#Add latitude and longitude columns to parcels_cincy table (point on centroid)
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$CODE_FOLDER/add_lat_long_to_parcels_cincy.sql"

#Create features
python "$CODE_FOLDER/census_features.py"