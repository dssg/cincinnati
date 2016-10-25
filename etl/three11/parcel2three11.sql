--Units for SRID 3735 are US survey foot
--https://en.wikipedia.org/wiki/Foot_(unit)#US_survey_foot
--1 US survey foot = 1200⁄3937 m
--1000 m ~ 3281 US survey foot
-- X [US Survey foot] / 3.281 ~ Y m
INSERT INTO last_updated_event
    (table_name, event_id)
    SELECT 'three11', 0
WHERE NOT EXISTS (
    SELECT table_name FROM last_updated_event WHERE table_name = 'three11'
);

DROP TABLE IF EXISTS parcel2three11;

-- find all the events within 1 km
CREATE TABLE parcel2three11 AS
SELECT
    parcels.parcelid AS parcel_id,
    three11.id AS event_id,
    ST_Distance(parcels.geom, three11.geom)/3.281 AS dist_m
FROM shape_files.parcels_cincy AS parcels
JOIN three11
ON ST_DWithin(parcels.geom, three11.geom, 3281);

--Create indexes on parcel_id and three11_id
CREATE INDEX three11_parcel_id_index ON parcel2three11 (parcel_id);
CREATE INDEX three11_event_id_index ON parcel2three11 (event_id);

--Update last_updated_event table
UPDATE last_updated_event
    SET event_id = (SELECT MAX(id) FROM three11)
    WHERE table_name = 'three11';
