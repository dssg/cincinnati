--Join parcel column in eac inspection in
--parcels_inspection (in whatever it is the current schema)
--with events that are within X Km (using parcel2TABLE table)
--then filter those addreses for events within 3 month of
--inspection date

--This script is intended to be used as a template for various tables
--Example for three11
CREATE TABLE insp_${N_MONTHS}months_${DATASET} AS (
    SELECT insp.parcel_id, insp.inspection_date, p2e.dist_km, event.*
    FROM features.parcels_inspections AS insp
    JOIN public.parcel2${DATASET} AS p2e
    USING (parcel_id)
    JOIN public.${DATASET} AS event
    ON ${DATASET}_id=event.id
    AND (insp.inspection_date - '${N_MONTHS}  month'::interval) <= event.${DATE_COLUMN}
    AND event.${DATE_COLUMN} <= insp.inspection_date
);



