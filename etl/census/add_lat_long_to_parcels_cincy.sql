--Add latitude and longitude columns to
--shape_files.parcels_cincy table

--Add columns
ALTER TABLE shape_files.parcels_cincy
ADD latitude float8,
ADD longitude float8;

--Set values
UPDATE shape_files.parcels_cincy AS parcels
SET
    latitude=ST_Y(ST_CENTROID(ST_TRANSFORM(parcels.geom, 4326))),
    longitude=ST_X(ST_CENTROID(ST_TRANSFORM(parcels.geom, 4326)));
