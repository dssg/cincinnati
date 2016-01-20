--Script for 311 feature generation
--Given the temporal natural of complains, we are going to generate features
--for each inspection by moving in two dimensions: date and distance.
--e.g. building complains within 1 km in a 3 month window from inspection date

--Join the parcels and complains table with the inspections table
--Generate one rows for each complain within X months on each inspection
WITH complains_in_time_window(
    SELECT *
    FROM features.parcels_inspections AS insp --change this
    JOIN parcels_and_complains AS pnc
    ON insp.parcel_id=pnc.parcelid
    AND (insp.inspection_date - '1 month'::interval) >= pnc.requested_datetime --complain date should be X months before insepction at most
    AND pnc.requested_datetime <= insp.inspection_date --and don't give me complains past the inspection date
)

--Now count each time of complain for each pacelid and inspection date
--SELECT count(service_code) FROM complains_in_time_window GROUP BY service_code