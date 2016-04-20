#!/usr/bin/env bash
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/inspections"
LOCAL_CODE_FOLDER="$ROOT_FOLDER/etl/inspections"
TMP_FOLDER="$LOCAL_DATA_FOLDER/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#Oracle DB auth
ORACLE_USER=system
ORACLE_PWD=oracle

#Build image from Dockerfile
docker build -t ora2pg .
echo 'Docker image built'

#Run container
docker run -d -p 49160:22 -p 49161:1521 -v $DATA_FOLDER/etl/inspections:/root/data ora2pg
#SSH to Docker
#password: admin
ssh root@localhost -p 49160

#For some reason this is not getting installed whe building
#perl -MCPAN -e 'install DBD::Oracle'

#Part 1: Export Oracle dump to SQL
#Create schema to upload dmp file
sqlplus -s $ORACLE_USER/$ORACLE_PWD@localhost <<< "create user inspections_raw identified by password default tablespace users;"
sqlplus -s $ORACLE_USER/$ORACLE_PWD@localhost <<< "grant connect to inspections_raw;"
sqlplus -s $ORACLE_USER/$ORACLE_PWD@localhost <<< "grant create table to inspections_raw;"
sqlplus -s $ORACLE_USER/$ORACLE_PWD@localhost <<< "grant unlimited tablespace to inspections_raw;"
#Import dmp file to Oracle database
imp SYSTEM/$ORACLE_PWD file=/root/data/inspections.dmp fromuser=DBADLS touser=inspections_raw
#Export data to PostgreSQL
ora2pg -t TABLE -n inspections_raw -o /root/data/tmp/inspections.tables.sql
nohup ora2pg -t COPY -n inspections_raw -o /root/data/tmp/inspections.data.sql

#Kill container

#Part 2: Upload inspections data
#Drop everything in case it already exists
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP VIEW  IF EXISTS inspections_views.events_and_lat_long;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP VIEW  IF EXISTS inspections_views.events_parcel_id;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP VIEW  IF EXISTS inspections_views.events;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP VIEW  IF EXISTS inspections_views.number_key2parcel_no;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$LOCAL_CODE_FOLDER/drop_inspections_tables.sql"
#Add schema
sed -i -e "1iSET SCHEMA 'inspections_raw';\\" "$TMP_FOLDER/inspections.tables.sql"
sed -i -e "1iSET SCHEMA 'inspections_raw';\\" "$TMP_FOLDER/inspections.data.sql"
#Upload data
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/inspections.tables.sql"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$TMP_FOLDER/inspections.data.sql"

#Part 3: Create inspections views
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$ROOT_FOLDER/etl/inspections/events_timeline.sql"

echo 'Done uploading inspections data to postgres!'