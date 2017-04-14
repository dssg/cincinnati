DROP TABLE IF EXISTS model_results.all_top_k;

CREATE TABLE model_results.all_top_k (
       parcel_id VARCHAR(14) NOT NULL, 
       prediction NUMERIC,
       inspection_density NUMERIC, 
       violation_rate NUMERIC,
       violations_per_house NUMERIC,
       model_group INT,
       subset VARCHAR
      
);



