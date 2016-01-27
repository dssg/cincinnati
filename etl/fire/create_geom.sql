--Create temporary table with a geom field
CREATE TEMP TABLE geo_fire AS (
    SELECT *, ST_SetSRID(ST_MakePoint(longitude, latitude),4326) AS geom from public.fire
);

--Drop original table
DROP TABLE IF EXISTS public.fire;

--Create new table with the same name as the original one
CREATE TABLE public.fire AS(
    SELECT * FROM  geo_fire
);

--Create an index
CREATE INDEX ON fire USING GIST (geom);
