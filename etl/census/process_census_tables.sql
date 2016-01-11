--This script performs some changes in the census tables
--mostly column renaming to match the code produced by the
--summer team

--Keep data only for Hamilton county
--Note: summer team made a subset based on the county,
--only data inside Cincinnati is needed, subsetting by Cincinnaty area
--instead of county would be better
DELETE FROM shape_files.census_tracts WHERE countyfp10!='061';
DELETE FROM shape_files.census_blocks_groups WHERE countyfp10!='061';
DELETE FROM shape_files.census_blocks WHERE countyfp10!='061';

--add block group to census_blocks table
--block group is the first character in the block id
--also add some other columns
CREATE TEMPORARY TABLE blocks AS(
    SELECT  *,
            SUBSTRING(blockce10 FROM 0 FOR 2) AS blkgrp,
            tractce10 AS tract,
            blockce10 AS block,
            ST_AREA(geom) AS area,
            ST_PERIMETER(geom) AS perimeter
    FROM shape_files.census_blocks

);

DROP TABLE shape_files.census_blocks;

CREATE TABLE shape_files.census_blocks AS(
    SELECT * FROM blocks
);

--changes for block groups table


--changes for tracts table

--TABLE: shape_files.census_tracts
--Name conversion
--NEW <- OLD
--gid - no change
--objectid <- ?
--tractce10 - no change
--shape_area - all zeros
--shape_len - all zeros
--tract?
--area?
--acres?
--perimeter?
--geom - no change
--The rest of the columns are dropped

--Join census blocks with census block groups
