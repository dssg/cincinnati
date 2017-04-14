DROP TABLE IF EXISTS model_results.feature_crosstabs;

CREATE TABLE model_results.feature_crosstabs(
    model_group VARCHAR,
    quantity VARCHAR,
    subset VARCHAR,
    feature VARCHAR,
    value NUMERIC);


