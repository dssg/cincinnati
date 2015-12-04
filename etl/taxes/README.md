# Tax Data

## Dumping the data into the database

The files provided to us by the city are fixed width text files and CSV files. The fields are defined in `tax_defs.py`. There is tax information from 2007-2015, and first we dump each file into its own table in the database. 

Each file was loaded into a pandas dataframe and then pushed to the database using `DataFrame.to_sql()`. An example for 2015 is shown in the IPython notebook `Extract2015Taxes.ipynb`. 

After pushing the data using pandas, we wanted to remove the case sensitive column names so we wrote a short Python script to generate a SQL query to achieve this. This script (for 2015) is here: `taxdb_fixes.py`.

## Correcting Parcel IDs

Next, we need to create a new column that we can use to match parcel IDs across databases. The format of parcel ID in the raw data files does not match. The SQL script that was used is `taxdb_modifications.sql`. Each table was modified to add a column with a parcel ID in the same format as used in the other databases. Analysis should use this `new_parcel_id` column.

## Generating new tables 

Finally, we made two tables for the home values and tax foreclosure data that include data for each year - `tax_foreclosure` and `tax_combined`. 