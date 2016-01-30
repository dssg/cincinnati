--Create unique id
ALTER TABLE three11 ADD id SERIAL;

--make it primary key, this will allso create an index
ALTER TABLE three11 ADD PRIMARY KEY (id);

--add column for geometry point
ALTER TABLE three11 ADD geom geometry;

--compute geom based on lat,long
UPDATE three11
    SET geom=ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude),4326), 3735);

--create index on date column
CREATE INDEX ON three11 (requested_datetime);