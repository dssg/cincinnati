DROP TABLE IF EXISTS model_results.parcel_info;

CREATE TABLE model_results.parcel_info(
    parcel_id VARCHAR,
    residential BOOLEAN,
    block INT,
    block_group INT,
    tract VARCHAR,
    nhood VARCHAR,
    latitude NUMERIC,
    longitude NUMERIC,
    address VARCHAR,
    last_interaction TIMESTAMP WITHOUT TIME ZONE,
    last_interaction_type VARCHAR,
    last_interaction_event VARCHAR);


