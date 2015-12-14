#!/usr/bin/env bash

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