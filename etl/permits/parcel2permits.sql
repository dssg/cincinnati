--match parcels to 311 events
CREATE TABLE parcel2permits AS (
    SELECT parcels.parcelid AS parcel_id, permits.id AS permits_id, ST_Distance(parcels.geom, permits.geom)/1000 AS dist_km
    FROM shape_files.parcels_cincy AS parcels
    JOIN permits
    ON ST_DWithin(parcels.geom, permits.geom, 3000) --meters
)

CREATE INDEX ON parcel2permits (parcel_id);
CREATE INDEX ON parcel2permits (permits_id);