--Join parcel column in eac inspection in
--parcels_inspection (in whatever it is the current schema)
--with events that are within X m (using parcel2TABLE table)
--then filter those addreses for events within 3 month of
--inspection date

--This script is intended to be used as a template for various tables
--Example for three11
CREATE TABLE ${TABLE_NAME} AS (
    WITH inspections_subset AS(
        SELECT * FROM features.parcels_inspections
        WHERE '${MIN_INSP_DATE}' <= inspection_date
        AND inspection_date <= '${MAX_INSP_DATE}'
    )
    SELECT insp.parcel_id, insp.inspection_date, p2e.dist_m,
            event.id --columns to select from event
    FROM inspections_subset AS insp
    JOIN public.parcel2${DATASET} AS p2e
    USING (parcel_id)
    JOIN public.${DATASET} AS event
    ON event_id=event.id
    AND (insp.inspection_date - '${N_MONTHS}  month'::interval) <= event.${DATE_COLUMN}
    AND event.${DATE_COLUMN} <= insp.inspection_date
    AND p2e.dist_m <= ${MAX_DIST}
);



