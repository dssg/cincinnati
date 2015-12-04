-- all relevant combinations of inspection date and tract
DROP TABLE dates_tract;
CREATE TEMPORARY TABLE dates_tract AS
(  SELECT inspection_date, tract
   FROM features_labelled_data_time AS labels
   JOIN shape_files.parcelid_blocks_grp_tracts_nhoods AS shape
   ON labels.parcel_id = shape.parcelid); 


CREATE TEMPORARY TABLE crimes_one_year_per_tract
AS (SELECT combinations.tract, combinations.inspection_date, count(*)
    FROM dates_tract AS combinations
    JOIN public.crime_geocoded AS crime
    ON crime.tract = combinations.tract
    WHERE crime.date_reported < combinations.inspection_date
    AND crime.date_reported > combinations.inspection_date - interval '1 year'
    GROUP BY combinations.tract, combinations.inspection_date);

CREATE TEMPORARY TABLE crime_rate_one_year_per_tract 
AS (
    SELECT crimes.tract, crimes.inspection_date, crimes.count / population.population AS crime_rate 
    FROM  crimes_one_year_per_tract AS crimes
    JOIN (SELECT tract, sum("P0010001") AS population
          FROM shape_files.census_pop_housing
          GROUP BY tract) AS population
    ON population.tract = crimes.tract);

CREATE TABLE features.crime 
AS (
  SELECT labels.parcel_id, labels.inspection_date, crimes.crime_rate AS crime_rate_past_year
  FROM features_labelled_data_time AS labels
  JOIN shape_files.parcelid_blocks_grp_tracts_nhoods AS shape
  ON labels.parcel_id = shape.parcelid
  JOIN crime_rate_one_year_per_tract AS crimes
  ON  shape.tract = crimes.tract 
  AND labels.inspection_date = crimes.inspection_date);

