--This script updates the distance from every parcel to every address in the
--address table

--Units for SRID 3735 are US survey foot
--https://en.wikipedia.org/wiki/Foot_(unit)#US_survey_foot
--1 US survey foot = 1200⁄3937 m
--1000 m ~ 3281 US survey foot
-- X [US Survey foot] / 3.281 ~ Y m

--Insert a record in last_updated_event in case it doesn't exist
INSERT INTO last_updated_event
    (table_name, event_id)
    SELECT 'address', 0
WHERE NOT EXISTS (
    SELECT table_name FROM last_updated_event WHERE table_name = 'address'
);

--Insert new records in parcel2address table
INSERT INTO parcel2address(
    parcel_id,
    address_id,
    dist_m
)
WITH new_addresses AS(
    --Subselect addresses that have not been used
    --using the last updated address
    SELECT * FROM address WHERE id > (SELECT event_id FROM last_updated_event WHERE table_name='address')
)
--Compute distances for new addresses
SELECT parcels.parcelid AS parcel_id, new_addresses.id AS address_id, ST_Distance(parcels.geom, new_addresses.geom)/3.281 AS dist_m
FROM shape_files.parcels_cincy AS parcels
JOIN new_addresses
ON ST_DWithin(parcels.geom, new_addresses.geom, 3281);

--Update last updated address id
UPDATE last_updated_event
    SET event_id = (SELECT MAX(id) FROM address)
    WHERE table_name = 'address';