#!/usr/bin/env bash

# Downloads hourly weather data for a given station
# Find the codes and available dates at ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv

# Inputs:

# Check for their existence
if [ $# -lt 3 ]
then
  echo "Three arguments required"
  exit 1
fi

#  1. Directory Name where you'll store the data
DIRNAME=$1
#  2. USAF code
USAF=$2
#  3. WBAN code 
WBAN=$3
 

# grab beginning and ending years for the given station
(cd $DIRNAME && wget -N 'ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-history.csv')
begin=$(cat ${DIRNAME}/isd-history.csv | grep -E "${USAF}.*${WBAN}" | cut -d, -f10 | cut -c2-5)
end=$(cat ${DIRNAME}/isd-history.csv | grep -E "${USAF}.*${WBAN}" | cut -d, -f11 | cut -c2-5)

parallel -j200% '(wget -N -P {1} "ftp://ftp.ncdc.noaa.gov/pub/data/noaa/isd-lite/{4}/{2}-{3}-{4}.gz")' ::: $DIRNAME ::: $USAF ::: $WBAN ::: $(seq $begin $end)
