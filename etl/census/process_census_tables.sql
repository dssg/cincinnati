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
CREATE TEMPORARY TABLE blocks_groups AS(
    SELECT  *,
            tractce10 AS tract,
            blkgrpce10 AS blkgrp,
            ST_AREA(geom) AS area,
            ST_PERIMETER(geom) AS perimeter
    FROM shape_files.census_blocks_groups

);

DROP TABLE shape_files.census_blocks_groups;

CREATE TABLE shape_files.census_blocks_groups AS(
    SELECT * FROM blocks_groups
);

--changes for tracts table