##ETL

Here you will find one subfolders for each dataset that we used. For each folder, a shell script (with the same name as the parent folder) is provided which performs the etl for that dataset.

For example, to load the cagis data, run:

`bash etl/cagis/cagis.sh`


## Before running ETL scripts setup the database

The data is organized in different schemas, before you start loading any data, run the following script.

`./db_setup.sh`

*Important:* it is assumed that you are using PostgreSQL with PostGIS installed as your database. Make sure that you have [PostGIS](http://postgis.net/) installed before proceeding. This is the only manual step you need to do.
