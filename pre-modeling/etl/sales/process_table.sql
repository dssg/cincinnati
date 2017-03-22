--Create unique id
ALTER TABLE sales ADD id SERIAL;

--make it primary key, this will allso create an index
ALTER TABLE sales ADD PRIMARY KEY (id);

--create index on date column
CREATE INDEX sales_date_index ON sales(date_of_sale);
