--Create a table that matches parcelid with 311 call id and compute the distance
--limit rows where the parcel and the call are 3 km long

--Should I make a distinction between calls close to a parcel and the ones
--INSIDE the parcel?
CREATE TABLE parcels_to_three11 AS (
    SELECT parcels.parcelid, three.service_request_id, ST_Distance(parcels.geom, three.geom)/1000 AS dist_km
    FROM shape_files.parcels_cincy AS parcels
    JOIN public.three11 AS three ON ST_DWithin(parcels.geom, three.geom, 3000) --meters
);
