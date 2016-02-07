--Table used to relate parcels with close addresses
CREATE TABLE parcel2address (
    parcel_id varchar(30) NOT NULL,
    address_id integer REFERENCES address,
    dist_m real NOT NULL
);

CREATE INDEX ON parcel2address (parcel_id);
CREATE INDEX ON parcel2address (address_id);
