--Create a table that performs countings on events for an inspections list
--counts are done using a certain distance and time window
--using this table we will identify interesting predictions in our model
--for example, true positives outside 'bad beighborhoods'
CREATE TABLE ${schema}.${table_name} AS(
    --First: attach geometry column to parcels_inspections table
    WITH inspections_location AS(
        SELECT insp.*, parcels.geom
        FROM ${schema}.parcels_inspections AS insp
        JOIN shape_files.parcels_cincy AS parcels
        ON insp.parcel_id=parcels.parcelid
    ),
    --Second: find inspections pairs that
    --ocurred within certain distance and time window
    --store the status of the second parcel
    matches AS (
        SELECT parcels_a.parcel_id, parcels_a.inspection_date, parcels_b.viol_outcome
        FROM inspections_location AS parcels_a
        JOIN inspections_location AS parcels_b
        ON ST_DWithin(parcels_a.geom, parcels_b.geom, ${max_dist_foot})
        AND (parcels_a.inspection_date - '${n_months} month'::interval) <= parcels_b.inspection_date
        AND parcels_b.inspection_date <= parcels_a.inspection_date
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
    
    --select * from counts
        
    --Get geometric column for the unique parcels in counts
    parcels_cincy_subset AS(
        SELECT parcelid, geom FROM shape_files.parcels_cincy WHERE parcelid IN (SELECT DISTINCT parcel_id  FROM counts)
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
    
    --join with the counts table
    scores AS (
        SELECT counts.*, parcels_nearby.houses
        FROM counts
        JOIN parcels_nearby
        USING (parcel_id)
    )
    
    --Last step, attach a column with ranks for each column
    SELECT scores.*,
    rank() OVER (ORDER BY violations) AS violations_rank,
    rank() OVER (ORDER BY non_violations) AS non_violations_rank,
    rank() OVER (ORDER BY houses) AS houses_rank,
    rank() OVER (ORDER BY inspections) AS inspections_rank
    FROM scores
);
