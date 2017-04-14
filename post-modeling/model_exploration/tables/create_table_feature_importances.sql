DROP TABLE IF EXISTS model_results.feature_importances;

CREATE TABLE model_results.feature_importances(
    feature VARCHAR NOT NULL,
    model_group INT NOT NULL,
    feature_importance NUMERIC);


