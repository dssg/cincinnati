--Units for SRID 3735 are US survey foot
--https://en.wikipedia.org/wiki/Foot_(unit)#US_survey_foot
--1 US survey foot = 1200⁄3937 m
--1000 m ~ 3281 US survey foot
-- X [US Survey foot] / 3.281 ~ Y m

--match parcels to 311 events
CREATE TABLE parcel2permits AS (
    SELECT parcels.parcelid AS parcel_id, permits.id AS permits_id, ST_Distance(parcels.geom, permits.geom)/3.281 AS dist_m
    FROM shape_files.parcels_cincy AS parcels
    JOIN permits
    ON ST_DWithin(parcels.geom, permits.geom, 3281)
);

CREATE INDEX ON parcel2permits (parcel_id);
CREATE INDEX ON parcel2permits (permits_id);
