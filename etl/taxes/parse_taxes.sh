#!/usr/bin/env bash

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