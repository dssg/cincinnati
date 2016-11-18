--Table used to relate parcels with close addresses
CREATE TABLE IF NOT EXISTS parcel2address (
    parcel_id varchar(30) NOT NULL,
    address_id integer REFERENCES address,
    dist_m real NOT NULL
);

CREATE INDEX parcel2address_parcel_id_index ON parcel2address (parcel_id);
CREATE INDEX parcel2address_address_id_index ON parcel2address (address_id);
CREATE INDEX parcel2address_dist_m_index ON parcel2address (dist_m);
