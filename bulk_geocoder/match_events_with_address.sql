--CRIME
CREATE TEMPORARY TABLE new_crime AS(
    SELECT event.*, addr.id AS address_id
    FROM crime AS event
    LEFT JOIN address AS addr
    USING (address)
);

DROP TABLE IF EXISTS crime;

CREATE TABLE crime AS(
    SELECT * FROM new_crime
);

CREATE INDEX ON crime (date_reported);
CREATE INDEX ON crime (address_id);

--FIRE
CREATE TEMPORARY TABLE new_fire AS(
    SELECT event.*, addr.id AS address_id
    FROM fire AS event
    LEFT JOIN address AS addr
    USING (address)
);

DROP TABLE IF EXISTS fire;

CREATE TABLE fire AS(
    SELECT * FROM new_fire
);

CREATE INDEX ON fire (date);
CREATE INDEX ON fire (address_id);

--SALES
CREATE TEMPORARY TABLE new_sales AS(
    SELECT event.*, addr.id AS address_id
    FROM sales AS event
    LEFT JOIN address AS addr
    USING (address)
);

DROP TABLE IF EXISTS sales;

CREATE TABLE sales AS(
    SELECT * FROM new_sales
);

CREATE INDEX ON sales (datesale);
CREATE INDEX ON sales (address_id);