--Create a table that performs countings on events for an inspections list
--counts are done using a certain distance and time window
--using this table we will identify interesting predictions in our model
--for example, true positives outside 'bad beighborhoods'


DROP TABLE IF EXISTS ${schema}.${table_name};

CREATE TABLE ${schema}.${table_name} AS(
    --First: attach geometry column to parcels_inspections table
    --in the current schema
    WITH schema_inspections_location AS(
        SELECT insp.*, parcels.geom
        FROM ${schema}.parcels_inspections AS insp
        JOIN shape_files.parcels_cincy AS parcels
        ON insp.parcel_id=parcels.parcelid
    ),
    --Do the same for the parcels_inspections table but in the features
    --schema, since this table contains the labels
    real_inspections_location AS(
        SELECT insp.*, parcels.geom
        FROM features.parcels_inspections AS insp
        JOIN shape_files.parcels_cincy AS parcels
        ON insp.parcel_id=parcels.parcelid
    ),

    --Second: find inspections pairs that
    --ocurred within certain distance and time window
    --store the status of the second parcel
    matches AS (
        --grab parcel_id and inspection_date for both
        --parcels, but only the outcome for the second one
        SELECT parcels_a.parcel_id AS parcel_id,
               parcels_a.inspection_date AS inspection_date,
               parcels_b.parcel_id AS parcel_id_b,
               parcels_b.inspection_date AS inspection_date_b,
               parcels_b.viol_outcome AS viol_outcome
        FROM schema_inspections_location AS parcels_a
        JOIN real_inspections_location AS parcels_b
        ON ST_DWithin(parcels_a.geom, parcels_b.geom, ${max_dist_foot})
        AND (parcels_a.inspection_date - '${n_months} month'::interval) <= parcels_b.inspection_date
        AND parcels_b.inspection_date < parcels_a.inspection_date
    ),
    
    --select * from matches

    --From the parcels pairs count how many had a violation, non-violation
    --and the total number of inspections
    counts AS (
        SELECT
            parcel_id,
            inspection_date,
            SUM(CASE WHEN viol_outcome = 1 THEN 1 ELSE 0 END) violations,
            SUM(CASE WHEN viol_outcome = 0 THEN 1 ELSE 0 END) non_violations,
            COUNT(*) AS inspections
        FROM matches
        GROUP BY parcel_id, inspection_date
    ),

    --Using matches, do the counting again, but this time
    --count events in the same parcel_id_b as one
    --this way we can avoid overcounting parcels that have been
    --inspected more than once for the given period
    --order by viol_outcome, so in case a parcel had multiple inspections
    --with different viol_outcome it's going to be counted as one
    --violation

    --Get unique matches
    unique_matches AS (
        SELECT
            DISTINCT ON (parcel_id, inspection_date, parcel_id_b, viol_outcome) *
            FROM matches
            ORDER BY viol_outcome DESC
    ),

    --Do the counting
    unique_counts AS (
        SELECT
            parcel_id,
            inspection_date,
            SUM(CASE WHEN viol_outcome = 1 THEN 1 ELSE 0 END) unique_violations,
            SUM(CASE WHEN viol_outcome = 0 THEN 1 ELSE 0 END) unique_non_violations,
            COUNT(DISTINCT parcel_id_b) AS unique_inspections
        FROM unique_matches
        GROUP BY parcel_id, inspection_date
    ),
    
    --select * from counts
        
    --Get geometric column for the unique parcels in counts
    parcels_cincy_subset AS(
        SELECT parcelid, geom
            FROM shape_files.parcels_cincy
            WHERE parcelid IN (SELECT DISTINCT parcel_id  FROM counts)
    ),

    --for those parcels, count the number of parcels nearby using
    --the table containing all parcels in cincinnati
    --(shape_files.parcels_cincy)
    parcels_nearby AS (
        SELECT parcels_a.parcelid AS parcel_id, COUNT(*) AS houses
        FROM parcels_cincy_subset AS parcels_a
        JOIN shape_files.parcels_cincy AS parcels_b
        ON ST_DWithin(parcels_a.geom, parcels_b.geom, ${max_dist_foot})
        GROUP BY parcel_id
    ),
    
    --join with the both counting tables
    scores AS (
        SELECT counts.*,
	       unique_counts.unique_violations,
	       unique_counts.unique_non_violations,
	       unique_counts.unique_inspections,
	       parcels_nearby.houses
        FROM counts
        JOIN unique_counts
        USING(parcel_id, inspection_date)
	JOIN parcels_nearby
	USING(parcel_id)
    )
    
    --Last step, attach a column with ranks for each column
    SELECT scores.*,
    rank() OVER (ORDER BY violations) AS violations_rank,
    rank() OVER (ORDER BY non_violations) AS non_violations_rank,
    rank() OVER (ORDER BY inspections) AS inspections_rank,

    rank() OVER (ORDER BY unique_violations) AS unique_violations_rank,
    rank() OVER (ORDER BY unique_non_violations) AS unique_non_violations_rank,
    rank() OVER (ORDER BY unique_inspections) AS unique_inspections_rank,

    rank() OVER (ORDER BY houses) AS houses_rank
    FROM scores
);

CREATE INDEX ON ${schema}.${table_name} (parcel_id, inspection_date);
