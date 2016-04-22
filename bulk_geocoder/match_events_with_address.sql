--Permits
--Create address_id column
ALTER TABLE permits
    ADD COLUMN address_id int4;

--Update rows that do not have an address_id value
--with the corresponding one in address table
UPDATE permits
    SET address_id = address.id
    FROM address
    WHERE permits.address = address.address
    AND permits.address_id IS NULL;

--Create index
CREATE INDEX permits_address_index ON permits (address_id);

--CRIME
--Create address_id column
ALTER TABLE crime
    ADD COLUMN address_id int4;

--Update rows that do not have an address_id value
--with the corresponding one in address table
UPDATE crime
    SET address_id = address.id
    FROM address
    WHERE crime.address = address.address
    AND crime.address_id IS NULL;

CREATE INDEX crime_address_index ON crime (address_id);

--FIRE
--Create address_id column
ALTER TABLE fire
    ADD COLUMN address_id int4;

--Update rows that do not have an address_id value
--with the corresponding one in address table
UPDATE fire
    SET address_id = address.id
    FROM address
    WHERE fire.address = address.address
    AND fire.address_id IS NULL;

CREATE INDEX fire_address_index ON fire (address_id);

--SALES
--Create address_id column
ALTER TABLE sales
    ADD COLUMN address_id int4;

--Update rows that do not have an address_id value
--with the corresponding one in address table
UPDATE sales
    SET address_id = address.id
    FROM address
    WHERE sales.address = address.address
    AND sales.address_id IS NULL;

CREATE INDEX sales_address_index ON sales (address_id);
