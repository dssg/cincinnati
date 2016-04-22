--Create unique id
ALTER TABLE permits ADD id SERIAL;

--make it primary key, this will allso create an index
ALTER TABLE permits ADD PRIMARY KEY (id);

--create index on date column
CREATE INDEX permits_date_index ON permits (issueddate);