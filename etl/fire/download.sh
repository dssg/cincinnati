#!/usr/bin/env bash
LOCAL_DATA_FOLDER="$DATA_FOLDER/etl/fire"
TMP_FOLDER="$LOCAL_DATA_FOLDER/tmp"

echo 'Downloading 2012 data...'
wget -O "$LOCAL_DATA_FOLDER/fire_2012.csv" https://data.cincinnati-oh.gov/api/views/e5f9-hc72/rows.csv?accessType=DOWNLOAD

echo 'Downloading 2013 data...'
wget -O "$LOCAL_DATA_FOLDER/fire_2013.csv" https://data.cincinnati-oh.gov/api/views/7xjr-6ajm/rows.csv?accessType=DOWNLOAD

echo 'Downloading 2014 data...'
wget -O "$LOCAL_DATA_FOLDER/fire_2014.csv" https://data.cincinnati-oh.gov/api/views/3ctx-y63h/rows.csv?accessType=DOWNLOAD

echo 'Downloading 2015 data...'
wget -O "$LOCAL_DATA_FOLDER/fire_2015.csv" https://data.cincinnati-oh.gov/api/views/96sp-aysv/rows.csv?accessType=DOWNLOAD

echo 'Concatenating files...'
awk 'FNR > 1' fire_201*.csv > content.csv
head -n1 fire_2012.csv > fire.csv
cat content.csv >> fire.csv
rm -f content.csv

echo 'Done.'