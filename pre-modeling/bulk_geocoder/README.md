# Geocoding

There are two types of data that include location:

*   Data with latitude and longitude (three11, permits)
*   Data with address only (fire, sales, crime)

For both groups we need to create PostGIS geometry columns. For datasets that already include lat long, the creation of PostGIS columns is done in their corresponding etl script.

However, for datasets with address only, we are merging the addresses to avoid the overhead of geocoding and computing features for each one. So once, the ETL for those is done, execute `geocode.sh`. The script assumes the files have certain names, but if ETL scripts haven't been modified it should work fine.

If new address-only datasets come in, they must be manually added to this step, it must be trivial to do so if they meet minimum criteria. (basically just having an address column).

For more information on how the geocode process works, see the comments in the `geocode.sh` script.