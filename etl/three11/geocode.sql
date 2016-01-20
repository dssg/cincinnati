--Create temporary table with a geom field
CREATE TEMP TABLE geo_three11 AS (
    SELECT *, ST_SetSRID(ST_MakePoint(x_coord, y_coord), 3735) AS geom from public.three11
);

--Drop original table
DROP TABLE IF EXISTS public.three11;

--Create new table with the same name as the original one
CREATE TABLE public.three11 AS(

--Select cincinnati only
-- SELECT geo_three11.*
-- FROM    geo_three11,
--         shape_files.cinc_city_boundary AS boundary
-- WHERE ST_Within(geo_three11.geom, boundary.geom)

--Select all
SELECT * FROM  geo_three11
)

--Create an index
CREATE INDEX ON geo_three11 USING GIST (geom);
