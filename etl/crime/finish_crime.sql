
--remove duplicates
CREATE TEMPORARY TABLE duplicate_incidents 
AS (SELECT incident_number
    FROM public.crime__latlong
    GROUP BY incident_number
   HAVING COUNT(*) > 1)

DELETE FROM public.crime__latlong
WHERE incident_number IN (SELECT incident_number FROM duplicate_incidents)

--join
CREATE TEMPORARY TABLE crime_geocoded__temp AS 
(SELECT crime.*, 
    geo.latitude, 
    geo.longitude, 
    ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude),4269), 3735) AS geom   --4269 is census latitude / longitude, 3735 is cincinnati
FROM public.crime AS crime
LEFT OUTER JOIN public.crime__latlong AS geo
ON crime.incident_number = geo.incident_number);

-- add also information on census block, tract, etc
CREATE TABLE public.crime_geocoded AS (
SELECT crime.*, census.block, census.tract, census.blkgrp
FROM crime_geocoded__temp AS crime
LEFT OUTER JOIN shape_files.census_blocks AS census
ON ST_WITHIN(crime.geom, census.geom));

--drop tmp table
DROP TABLE public.crime__latlong