#!/usr/bin/env bash
TMP_FOLDER="$DATA_FOLDER/etl/taxes/tmp"

bash "$ROOT_FOLDER/etl/taxes/upload_tax.sh" $TMP_FOLDER taxes_2007.csv taxes_2007