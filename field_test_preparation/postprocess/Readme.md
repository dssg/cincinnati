## What is this?

The modeling code can produce a list of properties, each with a probability of finding a evaluation if the property
were inspected on some specific date. This directory contains the sourcecode necessary to add further information such
 as address and date of last inspection to the list.

## How to use this?

1. Download all additional property info from the database by running

    ./download_parcel_info
    
2. Select your inspections list file and add the parcel data (file must have a parcel_id as its first column)

   ./add_parcel_info PATH_TO_INSPECTIONS_LIST
 