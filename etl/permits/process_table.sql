--Create unique id
ALTER TABLE permits ADD id SERIAL;

--make it primary key, this will allso create an index
ALTER TABLE permits ADD PRIMARY KEY (id);

--add column for geometry point
ALTER TABLE permits ADD geom geometry;

--compute geom based on lat,long
UPDATE permits
    SET geom=ST_Transform(ST_SetSRID(ST_MakePoint(longitude, latitude),4326), 3735);

--create index on date column
CREATE INDEX ON permits (issueddate);