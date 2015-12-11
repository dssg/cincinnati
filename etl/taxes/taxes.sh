#!/usr/bin/env bash
TAXES_FOLDER="$DATA_FOLDER/etl/taxes"
TMP_FOLDER="$DATA_FOLDER/etl/taxes/tmp"

#Read variables from config file
DB_HOST=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.host)
DB_USER=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.user)
DB_NAME=$(cat $ROOT_FOLDER'/config.yaml' | shyaml get-value db.database)

#Parse files from 2007 to 2014, first parameter is filename, second is year
#the python script automatically performs operations in the corresponding
#data folder and outputs the result in the corresponding tmp folder
python "$ROOT_FOLDER/etl/taxes/parse_text_tax_file.py" taxinfo2007.txt 2007
python "$ROOT_FOLDER/etl/taxes/parse_text_tax_file.py" taxinfo2008.txt 2008
python "$ROOT_FOLDER/etl/taxes/parse_text_tax_file.py" taxinfo2009.txt 2009
python "$ROOT_FOLDER/etl/taxes/parse_text_tax_file.py" taxinfo2010.txt 2010
python "$ROOT_FOLDER/etl/taxes/parse_text_tax_file.py" taxinfo2011.txt 2011
python "$ROOT_FOLDER/etl/taxes/parse_text_tax_file.py" taxinfo2012.txt 2012
python "$ROOT_FOLDER/etl/taxes/parse_text_tax_file.py" taxinfo2013.txt 2013
python "$ROOT_FOLDER/etl/taxes/parse_text_tax_file.py" taxinfo2014.txt 2014

#File from 2015 is a CSV, we only need to append the header
python "$ROOT_FOLDER/etl/taxes/add_header_csv_tax_file.py" Tax_Information2015.CSV 2015

#Create table in the database
#echo "Loading data from $TAXES_FOLDER"
#psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "DROP TABLE IF EXISTS taxes_2015;"
#Load taxes file and create sql table
#python "$ROOT_FOLDER/etl/taxes/extract_taxes_2015.py"
