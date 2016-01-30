--match parcels to 311 events
CREATE TABLE parcel2three11 AS (
    SELECT parcels.parcelid AS parcel_id, three11.id AS three11_id, ST_Distance(parcels.geom, three11.geom)/1000 AS dist_km
    FROM shape_files.parcels_cincy AS parcels
    JOIN three11
    ON ST_DWithin(parcels.geom, three11.geom, 3000) --meters
)

CREATE INDEX ON parcel2three11 (parcel_id);
CREATE INDEX ON parcel2three11 (three11_id);