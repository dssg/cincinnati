##ETL

Here you will find one subfolders for each dataset that we used. For each folder, a shell script named `run` is provided which performs the etl for that dataset (it also contains an explanation on each step performed). For example, to load the CAGIS data, run:

```bash
./etl/cagis/run
```

**Note:** Some ETL steps depend on others, there's no script to run them in order (ups), but running inspections, parcels, CAGIS, census first should work fine.

##Before running ETL scripts setup the database

The data is organized in different schemas, before you start loading any data, run the following script to automatically create them.

```bash
./db_setup.sh
```

If using the Dockerfile to run the ETL, make sure that you have a `$ROOT_FOLDER/etl/.pgpass` that gives the credentials to your Postgres DB in the standard `.pgpass` format.

*Important:* it is assumed that you are using PostgreSQL with PostGIS installed as your database. Make sure that you have [PostGIS](http://postgis.net/) installed before proceeding. This is the only manual step you need to do.
