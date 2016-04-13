--Units for SRID 3735 are US survey foot
--https://en.wikipedia.org/wiki/Foot_(unit)#US_survey_foot
--1 US survey foot = 1200⁄3937 m
--1000 m ~ 3281 US survey foot
-- X [US Survey foot] / 3.281 ~ Y m
INSERT INTO last_updated_event
    (table_name, event_id)
    SELECT 'three11_2', 0
WHERE NOT EXISTS (
    SELECT table_name FROM last_updated_event WHERE table_name = 'three11_2'
);

--Create table if doesn't exist
CREATE TABLE IF NOT EXISTS parcel2three11_2 (
    parcel_id varchar(20) NOT NULL,
    event_id int4 NOT NULL,
    dist_m float8 NOT NULL
);
--Create indexes on parcel_id and three11_id
CREATE INDEX three11_parcel_id_index ON parcel2three11 (parcel_id);
CREATE INDEX three11_event_id_index ON parcel2three11 (three11_id);
    
--Insert new rows into table
INSERT INTO parcel2three11_2(
    parcel_id,
    event_id,
    dist_m
)
WITH new_records AS (
    SELECT * FROM three11_2 WHERE id > (SELECT event_id FROM last_updated_event WHERE table_name='three11_2')
)
--subselect table with rows that have an id greater than the one stored in last_updated_event table
SELECT parcels.parcelid AS parcel_id, new_records.id AS event_id, ST_Distance(parcels.geom, new_records.geom)/3.281 AS dist_m
FROM shape_files.parcels_cincy AS parcels
JOIN new_records
ON ST_DWithin(parcels.geom, new_records.geom, 3281)

--Update last_updated_event table
UPDATE last_updated_event
    SET event_id = (SELECT MAX(id) FROM three11_2)
    WHERE table_name = 'three11_2';