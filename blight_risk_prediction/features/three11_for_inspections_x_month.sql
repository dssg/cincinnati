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
CREATE TABLE three11_for_inspections_1_month AS (
    SELECT insp.parcel_id, insp.inspection_date, pnc.requested_datetime, pnc.dist_km, pnc.service_code, pnc.agency_responsible
    FROM parcels_inspections AS insp --don't make any assumption on which schema to use
    JOIN public.parcels_three11_view AS pnc
    ON insp.parcel_id=pnc.parcelid
    AND (insp.inspection_date - '1 month'::interval) <= pnc.requested_datetime --complain date should be X months before insepction at most
    AND pnc.requested_datetime <= insp.inspection_date --and don't give me complains past the inspection date
)