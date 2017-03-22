--Create unique id
ALTER TABLE fire ADD id SERIAL;

--make it primary key, this will allso create an index
ALTER TABLE fire ADD PRIMARY KEY (id);

--create index on date column
CREATE INDEX fire_date_index ON fire(incident_date);
