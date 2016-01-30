--Table used to keep track of addresses that were aldready used to
--compute distances for each parcel
CREATE TABLE already_computed_addresses (
    address_id integer REFERENCES address
);