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

*Important:* it is assumed that you are using PostgreSQL with PostGIS installed as your database. Make sure that you have [PostGIS](http://postgis.net/) installed before proceeding.

You also will need to have `gnumeric` installed (the crime run script depends on `gnumeric`'s `ssconvert`).

##Re-Running the ETL and New Data Dumps

We received a new data dump from Cincinnati, and also need to re-ETL the existing data into a blank Postgres DB. After the steps above (i.e., running `db_setup.sh`), here's the steps we went through:

1. **Parcels**: Build the repo's main Dockerfile, and drop into it as described in the repo's main README. Make sure that `shyaml` is installed in the container! (It should be.) Inside the container, also make sure that you have a `~/.pgpass` with the DB credentials (it should have been copied there), and that it's permissions are 0600 (`chmod 0600 ~/.pgpass`). Then go to `~/code/etl/parcels` and run the `run` script. It works off the `HamcoParcelData.gdb`, `parcpoly.shp`, and `Parcpoly_with_Bldinfo.shp`, which we consider static.
2. **Crime**: Requires being updated with a data dump. The `run` script is able to add only those rows to the DB which are newer than the latest data in the DB. Previous years of crime data seem to have been delivered in individual files, but these have been manually concatenated into `$DATA_FOLDER/etl/crime/crime.csv`. Running the `run` script creates that file from `crime.xlsx` and loads the CSV. 

  When we received the data update in September/October 2016, we manually made sure we had an `address`, `city`, and `state` column (and populated them by processing the address field, as far as possible), copied the file to `$DATA_FOLDER/etl/crime` and then changed the filename in the `update.yaml`. Then, we executed the commands from the `run` script, except the part that's `ssconvert`s the `crime.xlsx` file (we don't work off this one for the update, so it's unnecessary), and the later parts generate the `CREATE TABLE` statements (as the table already exists). The previously auto-generated `CREATE TABLE` statements had chose too-short `varchar` types and a lot of not-null constraints that the new data failed, thus we also had to alter the postgres table before the upload went through. We updated the `csvsql` command to `--no-constraint`, so this shouldn't happen again. Be sure that you don't have empty columns, though.
