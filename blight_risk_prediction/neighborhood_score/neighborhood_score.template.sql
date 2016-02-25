--Create a table that assigns a 'neighborhood_score' to each parcel
--the score is simply the violation counts at a certain distance and time window
--using this table we will identify interesting predictions in our model
--for example, true positives outside 'bad beighborhoods'
CREATE TABLE ${schema}.${table_name} AS(
    --First: attach geo to parcels_inspections table
    WITH inspections_location AS(
        SELECT insp.*, parcels.geom
        FROM ${schema}.parcels_inspections AS insp
        JOIN shape_files.parcels_cincy AS parcels
        ON insp.parcel_id=parcels.parcelid
    ),
    --Second: find inspections pairs that
    --ocurred within certain distance and time window, and where the second
    --inspection had a violation
    matches AS (
        SELECT parcels_a.parcel_id, parcels_a.inspection_date--, parcels_a.viol_outcome,
               --parcels_a.parcel_id, parcels_a.inspection_date, parcels_b.viol_outcome
        FROM inspections_location AS parcels_a
        JOIN inspections_location AS parcels_b
        ON ST_DWithin(parcels_a.geom, parcels_b.geom, ${max_dist_foot})
        AND (parcels_a.inspection_date - '${n_months}'::interval) <= parcels_b.inspection_date
        AND parcels_b.inspection_date <= parcels_a.inspection_date
        AND parcels_b.viol_outcome=1
    ),

    --Third: count 
    scores AS (
        SELECT parcel_id, inspection_date, count(*) AS score
        FROM matches GROUP BY parcel_id, inspection_date
    )

    --Last step, attach a column with the rank and percentile
    SELECT score,
    ntile(100) over (ORDER BY score) AS percentile,
    rank() over (ORDER BY score) AS rank
    FROM scores
);
