#Geocoding

There are two types of data that include location:
    * Data with latitude and longitude (three11, permits)
    * Data with address only (fire, sales, crime)

For both groups we need to create PostGIS geometry columns. For datasets that already include latlong, the creation of PostGIS columns is done in their corresponding etl script.

However, for datasets with address only, we are merging the addresses to avoid the overhead of geocoding and later on, computing features. So once, the etl for those is done, execute `geocode.sh`. The script assumes the files have certain names, but if scripts haven't been modified it should work.

If new address-only datasets come in, they must be manually added to this step, it must be trivial to do so if they meet minimum criteria. (basically just having an address column).

**Important**: There is still some legacy geocoding code for the crime etl folder. But it should be easy to change that to use this code.