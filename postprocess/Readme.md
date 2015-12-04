## What is this?

The modeling code can produce a list of properties, each with a probability of finding a evaluation if the property
were inspected on some specific date. This directory contains the sourcecode necessary to add further information such
 as address and date of last inspection to the list.

## How to use this?

1. Download all additional property info from the database by running

    python -m postprocess/download_parcel_info
    
2. Add name of your predictions file and desired output file to `merge.py` and run

   python -m postprocess/merge
 