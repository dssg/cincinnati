CREATE TABLE parcels_to_fire AS (
    SELECT parcels.parcelid, fire.id, ST_Distance(parcels.geom, fire.geom)/1000 AS dist_km
    FROM shape_files.parcels_cincy AS parcels
    JOIN public.fire AS fire ON ST_DWithin(parcels.geom, fire.geom, 3000) --meters
);
