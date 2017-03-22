--Create unique id
ALTER TABLE crime ADD id SERIAL;

--make it primary key, this will allso create an index
ALTER TABLE crime ADD PRIMARY KEY (id);

--create index on date column
CREATE INDEX crime_date_index ON crime(occurred_on);
