#!/usr/bin/env bash
CODE_FOLDER="$ROOT_FOLDER/etl/taxes"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#1. Parse raw taxes data files and generate CSVs
bash "$ROOT_FOLDER/etl/taxes/parse_taxes.sh"

#2. Upload CSVs to the database
#Get tmp folder for taxes etl
TMP_FOLDER="$DATA_FOLDER/etl/taxes/tmp"
#Upload taxes to the database, parameters are: folder where csv files are located
#csv file names and name for the table that will be created
bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2007.csv taxes_2007
bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2008.csv taxes_2008
bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2009.csv taxes_2009
bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2010.csv taxes_2010
bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2011.csv taxes_2011
bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2012.csv taxes_2012
bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2013.csv taxes_2013
bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2014.csv taxes_2014
bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2015.csv taxes_2015

#Run fixes on the db
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$CODE_FOLDER/taxdb_modifications.sql"  

#Delete some weird values in taxes_2008 and taxes_2009
echo 'Deleting weird values from 2008 and 2009 taxes...'
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DELETE FROM taxes_2008 WHERE taxes_paid NOT LIKE '0%';"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DELETE FROM taxes_2009 WHERE taxes_paid NOT LIKE '0%';" 
#Cast forcl flags to boolean
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "ALTER TABLE taxes_2008 ALTER forcl_flag \
TYPE boolean USING CASE forcl_flag WHEN 'Y' THEN TRUE WHEN 'N' THEN FALSE END;"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "ALTER TABLE taxes_2009 ALTER forcl_flag \
TYPE boolean USING CASE forcl_flag WHEN 'Y' THEN TRUE WHEN 'N' THEN FALSE END;"

#Join taxes tables, drops old table if exists
#join_taxes.sql creates tax_combined
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$CODE_FOLDER/join_taxes.sql"  
#Create tax_foreclosure tables
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < "$CODE_FOLDER/tax_foreclosure.sql"  
