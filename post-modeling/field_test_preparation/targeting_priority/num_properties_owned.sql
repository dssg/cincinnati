-- will use table parcels_inspections to get list of all parcels for which to calculate num_properties_owned
-- resulting table "targeting_priority" will also be stored in this table
SET SCHEMA 'features_01Aug2015';

-- how many properties does an organization / person own in year 2015
CREATE TEMPORARY TABLE owner_counts AS
(SELECT owner_name, count(*)
 FROM public.taxes_2015
 GROUP BY owner_name
 ORDER BY count(*) DESC);

-- for every parcel/inspection pair create a row in targeting_priority table
-- currently does not depend on inspection date, will always go for owner_2015
CREATE TABLE targeting_priority AS(
  SELECT parcel_id, inspection_date, count AS num_properties_owned
  FROM parcels_inspections as labels
  JOIN public.taxes_2015 AS taxes
  ON labels.parcel_id = taxes.new_parcel_id
  JOIN owner_counts as owners
  ON owners.owner_name = taxes.owner_name);