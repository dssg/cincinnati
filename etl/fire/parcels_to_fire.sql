CREATE TABLE parcels_to_fire AS (
    SELECT parcels.parcelid, three.service_request_id, ST_Distance(parcels.geom, three.geom)/1000 AS dist_km
    FROM shape_files.parcels_cincy AS parcels
    JOIN public.three11 AS three ON ST_DWithin(parcels.geom, three.geom, 3000) --meters
);
