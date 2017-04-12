DROP TABLE IF EXISTS model_results.all_top_k;

CREATE TABLE model_results.all_top_k (
       parcel_id VARCHAR(14) NOT NULL, 
       prediction NUMERIC,
       violation_rate DECIMAL,
       inspection_density DECIMAL,
       latitude DECIMAL,
       longitude DECIMAL,
       model_group INT,
       subset VARCHAR, 
       violations_per_house DECIMAL
);

\COPY model_results.all_top_k FROM all_top5.csv WITH CSV HEADER;

