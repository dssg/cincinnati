--This script updates the distance from every parcel to every address in the
--address table

--Units for SRID 3735 are US survey foot
--https://en.wikipedia.org/wiki/Foot_(unit)#US_survey_foot
--1 US survey foot = 1200⁄3937 m
--1000 m ~ 3281 US survey foot
-- X [US Survey foot] / 3.281 ~ Y m

--Get pending addresses
--http://stackoverflow.com/questions/22702388/improve-postgresql-set-difference-efficiency
WITH pending_addresses AS (
    SELECT * FROM address WHERE id NOT IN (SELECT address_id FROM already_computed_addresses) AND geom IS NOT NULL
),

computed_distances AS (
    SELECT parcels.parcelid AS parcel_id,
           address.id AS address_id,
           ST_Distance(parcels.geom, address.geom)/3.281 AS dist_m
    FROM shape_files.parcels_cincy AS parcels
    JOIN pending_addresses AS address ON ST_DWithin(parcels.geom, address.geom, 3281)
)

--Add computed addresses ids
INSERT INTO parcel2address
    SELECT * FROM computed_distances;

--Add ids
--we need this since we cannot rely only on the ids in computed_distances
--it may be the case that some events are close to zero parcels,
--I don't think there are many (maybe the one outside cincinnati)
--but this is a simple solution
INSERT INTO already_computed_addresses
    SELECT address_id FROM pending_addresses;