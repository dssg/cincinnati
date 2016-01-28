--This script updates the distance from every parcel to every address in the
--address table

--Get pending addresses
--http://stackoverflow.com/questions/22702388/improve-postgresql-set-difference-efficiency
WITH pending_addresses AS (
    SELECT * FROM address WHERE id NOT IN (SELECT address_id FROM already_computed_addresses) AND geom IS NOT NULL
),

computed_distances AS (
    SELECT parcels.parcelid AS parcel_id, address.id AS address_id, ST_Distance(parcels.geom, address.geom)/1000 AS dist_km
    FROM shape_files.parcels_cincy AS parcels
    JOIN pending_addresses AS address ON ST_DWithin(parcels.geom, address.geom, 3000) --meters
)

--Add computed addresses ids
INSERT INTO parcel2address
    SELECT * FROM computed_distances;
