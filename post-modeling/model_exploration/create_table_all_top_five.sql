DROP TABLE IF EXISTS all_top_five;

CREATE TABLE all_top_five (
       model_number VARCHAR(29) NOT NULL, 
       parcel_id VARCHAR(14) NOT NULL, 
       prediction DECIMAL NOT NULL, 
       violation_rate DECIMAL, 
       inspection_density DECIMAL, 
       latitude DECIMAL, 
       longitude DECIMAL, 
       violations_per_house DECIMAL
);

\COPY all_top_five FROM all_top5.csv WITH CSV HEADER;