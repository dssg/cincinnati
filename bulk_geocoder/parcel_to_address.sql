--Table used to relate parcels with close addresses
CREATE TABLE parcel2address (
    parcel_id varchar(30) NOT NULL,
    address_id integer REFERENCES address,
    dist_km real NOT NULL
);