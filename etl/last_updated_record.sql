--This table keeps track of the last record
--used for computing distances to avoid recomputations
--after datasets are updated
CREATE TABLE last_updated_record (
    table_name varchar(50) NOT NULL UNIQUE,
    record_id integer DEFAULT 0
);