#!/usr/bin/env bash
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/inspections"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#Creates table on default schema (generally this is the public schema)
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS bld_info;"  
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$LOCAL_DATA_FOLDER/auditor_building_info.tables.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$LOCAL_DATA_FOLDER/auditor_building_info.data.sql"


#Creates tables on inspections schema:
#t_dssg_csv_enf_viol and t_dssg_csv_enf_insp
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS inspections.t_dssg_csv_enf_viol;"  
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS inspections.t_dssg_csv_enf_insp;"  
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$LOCAL_DATA_FOLDER/cag_code_violations.tables.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$LOCAL_DATA_FOLDER/cag_code_violations.data.sql"

#Creates tables on inspections_raw schema
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$LOCAL_DATA_FOLDER/drop_raw_vendor_tables.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$LOCAL_DATA_FOLDER/raw_vendor_tables.tables.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$LOCAL_DATA_FOLDER/raw_vendor_tables.data.sql"

#Create view on inspections
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/etl/inspections/events_timeline.sql"