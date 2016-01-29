--Join parcels in parcels_inspection (in whatever it is the current schema)
--with addresses that are within 3Km
--then filter those addreses for events within 1 month of
--inspection date


--Script for 311 feature generation
--Given the temporal natural of complains, we are going to generate features
--for each inspection by moving in two dimensions: date and distance.
--e.g. building complains within 1 km in a 3 month window from inspection date
--in the ETL step, a table was generated to match parcels with 311 calls within 3 km
--in this one, we match those nearby calls with specific inspections in a one month interval
--IMPORTANT: note that this script does not make any assumption on which schema
--is going to be created and which parcels_inspections table is going to use,
--the only assumption is that the parcels_three11_view view exists in the public schema

--Join the parcels and complains table with the inspections table
--Generate one rows for each complain within X months on each inspection


CREATE TABLE events_3months_fire AS (
    SELECT
        insp.parcel_id, insp.inspection_date,
        p2a.dist_km,
        fire.*
    FROM features.parcels_inspections AS insp
    JOIN parcel2address AS p2a
    USING (parcel_id) --match one
    JOIN address
    ON address_id=address.id
    JOIN fire
    ON address.address=fire.address --THIS IS SLOW, maybe change for an ID or simply add index
    AND (insp.inspection_date - '3 month'::interval) <= fire.date
    AND fire.date <= insp.inspection_date
);

