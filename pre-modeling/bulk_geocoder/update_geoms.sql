--This script updates the address table looking for rows that still don't
--have a value in the geom column
UPDATE address
SET geom=ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude),4326), 3735)
WHERE latitude IS NOT NULL
AND longitude IS NOT NULL
AND geom IS NULL;
