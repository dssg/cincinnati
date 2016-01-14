--Rename some wkb_geometry columns to geom
--so all tables have the same name for the geographic column
ALTER TABLE shape_files.cinc_city_boundary
  RENAME COLUMN wkb_geometry TO geom;

ALTER TABLE shape_files.cinc_community_council_nhoods
  RENAME COLUMN wkb_geometry TO geom;

ALTER TABLE shape_files.cinc_sna_boundary_2010
  RENAME COLUMN wkb_geometry TO geom;

ALTER TABLE shape_files.cinc_zoning
  RENAME COLUMN wkb_geometry TO geom;

--select all parcels in Hamilton county that are within the Cincinnati city boundry
CREATE TABLE shape_files.parcels_cincy as 
(SELECT parcels.*
FROM	shape_files.hamilton_parcels as parcels,
		shape_files.cinc_city_boundary as city_boundry
WHERE ST_Within(parcels.geom, city_boundry.geom));

--rename some columns on parcels_cincy
ALTER TABLE shape_files.parcels_cincy
  RENAME COLUMN shape_area TO area;

--spatial index for new table
CREATE INDEX ON shape_files.parcels_cincy USING gist(geom);

--join parcels in Cincinnaty to blocks, block groups, tracts and neighborhoods
--select parcels in census blocks
CREATE TABLE shape_files.parcelid_blocks_groups_tracts as
(SELECT parcels.parcelid, parcels.addrno, parcels.addrst, parcels.addrsf, blocks.block, blocks.blkgrp, blocks.tract, parcels.geom
FROM	shape_files.parcels_cincy as parcels,
		shape_files.census_blocks as blocks
WHERE	st_contains(blocks.geom, ST_Centroid(parcels.geom))); 

--select census tracts in neighborhoods
CREATE TABLE shape_files.tracts_nhoods as
(SELECT tracts.tractce10 as tract, 
	(select nhoods.sna_name from shape_files.cinc_sna_boundary_2010 as nhoods 
	order by st_area(st_intersection(tracts.geom, nhoods.geom)) desc limit 1)
FROM	shape_files.census_tracts as tracts);

--join both tables to create main table of parcels, blocks, block groups, tracts, nhoods
CREATE TABLE shape_files.parcelid_blocks_grp_tracts_nhoods as
(SELECT pid_bt.parcelid as parcelid, 
		pid_bt.addrno as addrno, 
		pid_bt.addrst as addrst, 
		pid_bt.addrsf as addrsf, 
		pid_bt.block as block, 
		pid_bt.blkgrp as block_group,
		pid_bt.tract as tract,
		trc_nh.sna_name as nhood,
		pid_bt.geom as geom
FROM shape_files.parcelid_blocks_groups_tracts as pid_bt
JOIN shape_files.tracts_nhoods as trc_nh
on pid_bt.tract = trc_nh.tract);

--spatial index for new table
CREATE INDEX ON shape_files.parcelid_blocks_grp_tracts_nhoods USING gist(geom);

-- there are five parcels of which there are duplicates in the mapping table, just select one of the two rows for each of those
CREATE TEMPORARY TABLE unique_parcel_tracts AS (
SELECT DISTINCT ON (parcelid) * 
FROM shape_files.parcelid_blocks_grp_tracts_nhoods);

-- duplicates here too, deal with them some other time
-- for now, just exclude those from the query
CREATE TEMPORARY TABLE duplicate__parcels_cincy
AS (SELECT parcelid
FROM shape_files.parcels_cincy
GROUP BY parcelid
HAVING COUNT(*) > 1)

-- make mapping table that has lat and lon filled out
CREATE TABLE shape_files.parcelid_blocks_grp_tracts_nhoods___with_lat_lon AS (
SELECT tracts.*,
       ST_Y(ST_CENTROID(ST_TRANSFORM(parcels.geom, 4326))) AS latitude,
       ST_X(ST_CENTROID(ST_TRANSFORM(parcels.geom, 4326))) as longitude
FROM shape_files.parcels_cincy AS parcels
JOIN unique_parcel_tracts AS tracts
ON parcels.parcelid = tracts.parcelid
WHERE parcels.parcelid NOT IN (SELECT parcelid FROM duplicate__parcels_cincy));

CREATE INDEX ON shape_files.parcelid_blocks_grp_tracts_nhoods___with_lat_lon USING gist(geom);

-- double check that numbers match up
SELECT count(parcelid), count(distinct(parcelid))
FROM unique_parcel_tracts;

SELECT count(parcelid), count(distinct(parcelid))
FROM shape_files.parcels_cincy
WHERE parcelid NOT IN (SELECT parcelid FROM duplicate__parcels_cincy);

SELECT count(parcelid), count(distinct(parcelid))
FROM shape_files.parcelid_blocks_grp_tracts_nhoods___with_lat_lon;

-- copy new table over old one
DROP TABLE shape_files.parcelid_blocks_grp_tracts_nhoods;
ALTER TABLE shape_files.parcelid_blocks_grp_tracts_nhoods___with_lat_lon
  RENAME TO parcelid_blocks_grp_tracts_nhoods;

-- index on parcel id 
CREATE INDEX tracts_nhoods__parcelid_idx ON shape_files.parcelid_blocks_grp_tracts_nhoods(parcelid);
