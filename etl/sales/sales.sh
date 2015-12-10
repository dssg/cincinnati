#!/usr/bin/env bash
SALES_FOLDER="$DATA_FOLDER/etl/sales"
TMP_FOLDER="$DATA_FOLDER/etl/sales/tmp"

#mkdir if not exists
mkdir -p $TMP_FOLDER

echo "Converting data from $SALES_FOLDER"

#Convert raw data to tsv
python "$ROOT_FOLDER/etl/sales/extract.py" "$SALES_FOLDER/salesinfo.txt" > "$TMP_FOLDER/salesinfo.tsv"
#transform data and export to csv
python "$ROOT_FOLDER/etl/sales/transform.py" "$TMP_FOLDER/salesinfo.tsv" "$TMP_FOLDER/salesinfo.csv"