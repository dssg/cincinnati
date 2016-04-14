--This table is going to be used to store ALL different addresses
--in the different datasets we have, this way we will significantly reduce
--the number of distance computations
CREATE TABLE IF NOT EXISTS address (
    --Create an unique id
    id SERIAL PRIMARY KEY,
    --address: number and street name
    --this should be unique in the table
    address varchar(100) NOT NULL UNIQUE,
    zip varchar(10),
    latitude float8,
    longitude float8,
    --coordinates, make sure they are in the 3735 SRID
    --x_coord int4,
    --y_coord int4,
    --geometry
    geom geometry
);

CREATE INDEX address_id_index ON address (id);
CREATE INDEX address_geom_index ON address USING GIST (geom);