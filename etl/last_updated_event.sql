--This table keeps track of the last record
--used for computing distances to avoid recomputations
--after datasets are updated
CREATE TABLE last_updated_event (
    table_name varchar(50) NOT NULL UNIQUE,
    event_id integer DEFAULT 0
);