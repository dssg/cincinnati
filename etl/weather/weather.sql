drop table if exists input.weather;

CREATE TABLE input.weather (
	year INTEGER NOT NULL, 
	month VARCHAR(2) NOT NULL, 
	day VARCHAR(2) NOT NULL, 
	hour VARCHAR(2) NOT NULL, 
	air_temp INTEGER, 
	dew_point_temp VARCHAR(4), 
	sea_level_pressure INTEGER, 
	wind_direction INTEGER, 
	wind_speed_rate INTEGER, 
	sky_condition_total_coverage_code INTEGER, 
	liquid_precipitation_depth_dimension_one_hour INTEGER, 
	liquid_precipitation_depth_dimension_six_hours INTEGER
);
