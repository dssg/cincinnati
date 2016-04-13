--Units for SRID 3735 are US survey foot
--https://en.wikipedia.org/wiki/Foot_(unit)#US_survey_foot
--1 US survey foot = 1200⁄3937 m
--1000 m ~ 3281 US survey foot
-- X [US Survey foot] / 3.281 ~ Y m

--match parcels to 311 events
CREATE TABLE parcel2three11 AS (
    SELECT parcels.parcelid AS parcel_id, three11.id AS three11_id, ST_Distance(parcels.geom, three11.geom)/3.281 AS dist_m
    FROM shape_files.parcels_cincy AS parcels
    JOIN three11
    ON ST_DWithin(parcels.geom, three11.geom, 3281)
);

CREATE INDEX three11_parcel_id_index ON parcel2three11 (parcel_id);
CREATE INDEX three11_event_id_index ON parcel2three11 (three11_id);