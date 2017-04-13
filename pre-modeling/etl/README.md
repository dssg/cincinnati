## Docker Setup

### Build Docker ETL image

The ETL step depends on these programs:

* Python 2.7.11
* GDAL 1.11.2
* Java 1.8
* psql (PostgreSQL) 9.3.10
* PostGIS 2.1.4
* mdbtools 0.7.1 
* gnumeric 1.12.9
* stanford-ner-2015-12-09
* ...and many Python packages

To ease the setup, a Dockerfile is provided which builds an Ubuntu 14.04 image with all dependencies included and properly configured.

Most dependencies are needed for the ETL step, after the raw data is on the database, only Python (and a few packages) and psql is needed, hence, if you want, you can use the Docker image for the ETL phase only. For information on how to setup Docker, see the [official docs](https://docs.docker.com/).

Once Docker is properly setup, go to your `$ROOT_FOLDER` and run:

```bash
docker build -t cincinnati .
```

This process takes a while since it needs to download and install all dependencies, but with a decent internet connection is should take less than 1 hour.

### Run Docker image

Once the image is ready, run it: 

```bash
docker run -v $DATA_FOLDER:/root/data -v $ROOT_FOLDER:/root/code -v $OUTPUT_FOLDER:/root/output -i -t cincinnati /bin/bash
```

Note that we are passing our three environment variables, and linking them to three folders inside the container. The purpose of the Docker container is to run code but not to store anything (not code and of course not data).

### Organize Data According to Repo Structure

The ETL code and the data folders need to follow a similar convention. It is assumed that a file in `$ROOT_FOLDER/pre-modeling/etl/something/` will get its raw data from `$DATA_FOLDER/etl/something/`.

It should be straightforward to know where to store the raw data. For example, the code that loads all taxes data is `$ROOT_FOLDER/etl/taxes/taxes.sh`, then, your raw taxes files should be stores in `$DATA_FOLDER/etl/taxes/`

The other convention is that intermediate files are stored on a `tmp/` folder, for example, since we need to preprocess the taxes files before uploading them to the database, the intermediate csv files will be on `$DATA_FOLDER/etl/taxes/tmp/`.


## ETL

Here you will find one subfolders for each dataset that we used. For each folder, a shell script named `run` is provided which performs the etl for that dataset (it also contains an explanation on each step performed). For example, to load the CAGIS data, run:

```bash
./etl/cagis/run
```

**Note:** Some ETL steps depend on others. There's no script to run them in order, but running inspections, parcels, CAGIS, census first should work fine.

## Before running ETL scripts setup the database

The data is organized in different schemas, before you start loading any data, run the following script to automatically create them.

```bash
./db_setup.sh
```

If using the Dockerfile to run the ETL, make sure that you have a `$ROOT_FOLDER/etl/.pgpass` that gives the credentials to your Postgres DB in the standard `.pgpass` format.

*Important:* it is assumed that you are using PostgreSQL with PostGIS installed as your database. Make sure that you have [PostGIS](http://postgis.net/) installed before proceeding.

You also will need to have `gnumeric` installed (the crime run script depends on `gnumeric`'s `ssconvert`).

## Re-Running the ETL and New Data Dumps

We received a new data dump from Cincinnati in September 2016. At that time, we also needed to re-run all ETL to upload the data into a new (blank) Postgres database. After the steps above (i.e., running `db_setup.sh`), here's the steps we went through:

1. **Parcels**: Build the repo's main Dockerfile, and drop into it as described above in this README. Make sure that `shyaml` is installed in the container! (It should be.) Inside the container, also make sure that you have a `~/.pgpass` with the DB credentials (it should have been copied there), and that it's permissions are 0600 (`chmod 0600 ~/.pgpass`). Then go to `~/code/etl/parcels` and run the `run` script. It works off the `HamcoParcelData.gdb`, `parcpoly.shp`, and `Parcpoly_with_Bldinfo.shp`, which we consider static.

2. **Crime**: Requires being updated with a data dump. The `run` script is able to add only those rows to the DB which are newer than the latest data in the DB. Previous years of crime data seem to have been delivered in individual files, but these have been manually concatenated into `$DATA_FOLDER/etl/crime/crime.csv`. Running the `run` script creates that file from `crime.xlsx` and loads the CSV.
When we received the data update in September/October 2016, we manually made sure we had an `address`, `city`, and `state` column (and populated them by processing the address field, as far as possible), copied the file to `$DATA_FOLDER/etl/crime` and then changed the filename in the `update.yaml` to that of the newly delivered file. Then, we executed the commands from the `run` script, except the part that `ssconvert`s the `crime.xlsx` file (we don't work off this one for the update, so it's unnecessary), and the later parts generate the `CREATE TABLE` statements (as the table already exists). The previously auto-generated `CREATE TABLE` statements had chose too-short `varchar` types and a lot of not-null constraints that the new data failed, thus we also had to alter the postgres table before the upload went through. We updated the `csvsql` command to `--no-constraint`, so this shouldn't happen again. Be sure that you don't have empty columns, though.
  
3. **CAGIS**: After some bugfixes, the `run` script works. This data was not updated in September 2016.

4. **Census**: After some bugfixes, the `run` script works. This data was not updated in September 2016. Some of the downloaded files are already present in the data folders, and we didn't overwrite them.

5. **Inspections**: This data was delivered as an Oracle dump ('DSSG_Data.dmp'). It seems that these dumps are cummulative - we only need to load the latest dump, which includes all previous data, as well. The loading is run via the docker container in `etl/inspections/`. The `run_new.sh` script contains all the steps that need to be executed - that file isn't a script really, though, but instead lists which commands you need to execute on your local (host) machine, and which ones in the Docker container itself. Those commands read the `inspections.dmp` file in the `$DATA_FOLDER/etl/inspections/`; if you have a new file, you need to modify the commands accordingly.

6. **Fire**: The existing data is being pulled from Cincinnati's open data API. However, we got a new data dump in September 2016, covering the first 10 months of 2016, which were not yet available via the API. Adding this file as `$DATA_FOLDER/etl/fire/fire_2016_10_13.csv`, and then running the `etl/fire/run` script (with some changes to the scripts) did the job.

7. **Permits**: This data wasn't updated in our data refresh; the `etl/permits/run` script did it for the existing data.

8. **Taxes**: The house pricing data becomes available only at the end of year; as our data refresh fell into September 2016, and the last data that had been delivered for 2015; no data needed to be updated. The `run` script worked for the data that had been previously delivered.

9. **Sales**: In September/October 2016, we received a new file of sales data, called `Salesinfo.exe`. We manually unzipped it into `salesinfo_sept2016.txt`, a CSV file. It seems that this file is complete (it lists all sales data from the beginning of time to October 2016). While the ETL is written such that it only adds those rows from a file that are newer than the currently newest row in the DB, it seems that this new file (`salesinfo_sept2016.txt`) contains _more_ rows even for previous years than the last delivered file. This seems to be incrementally true for the previously delivered file, as well; there is some continous back-filling of data happening on Cincinnati's part. We thus dropped the existing `sales` table, and ran the `run` script on the new data delivery, taking that as our new standard. Note: Only around ~57% of rows were successfully geocoded by the script.

10. **Food Safety**: Isn't used as a feature, so we don't load this data again. The file that had been ETL-ed previously (`od_cinc_food_safety.xls`) lists data for 2012 only, anyway. If this data is interesting to us, we should use Cincinnati's open data API, which now also provides the outcome of food inspections.

11. **Water Shutoff**: Not used as a feature currently; we didn't load the old data again.

12. **NER**: Has to be run in the repo's main Dockerfile; (almost) worked out of the box. This is running off the tax data, which we had updated.

13. **Three11**: This pulls updated data from the API. The only problem here was that the `run` script generates a huge (1.4bn rows) lookup table that links events to parcels. This table takes a few hours to build; creating the index on it takes a day or two. The script only inserts new rows into this table; this is good if you're just updating data, but slow if you're building the table from scratch.

14. **Building Info**: This is a table that was provided initially (in summer 2015) as part of the inspections Oracle dump. Then, in April 2016, this data was updated via a delivery as a CSV file (`data-refresh/april-2016/bldinfo.txt`). This later file was never loaded, as it seems very similar to the initially delivered table from the Oracle dump. We should still ETL it at some point. For now, we just re-loaded the old table, using the SQL extracts from the Oracle dump (that the summer 2015 probably created by hand) and which are loaded by Part 1 of the `etl/inspections/run` script.

Before running the `featurebot`, we also need to run `/bulk_geocoder/run`, as that created some tables the `featurebot` expected. Note that the bulk geocoder relies on some of the `tmp` folders (and the files therein) that are being created while running the ETL - so don't delete them!
