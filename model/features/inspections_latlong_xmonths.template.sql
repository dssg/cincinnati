--Join parcel column in each inspection in
--parcels_inspection (in whatever it is the current schema)
--with events that are within X m (using parcel2TABLE table)
--then filter those addreses for events within n month of
--inspection date

--This script is intended to be used as a template for various tables
--Example for three11
CREATE TABLE ${TABLE_NAME} AS (
	--schema is not specified here
	--since the db connection should set one
	--using SET SCHEMA
    SELECT insp.parcel_id, insp.inspection_date, p2e.dist_m,
            event.id --columns to select from event, limited in WHERE clause below
    FROM parcels_inspections AS insp
    JOIN public.parcel2${DATASET} AS p2e
    USING (parcel_id)
    JOIN public.${DATASET} AS event
    ON event_id=event.id
    AND (insp.inspection_date - '${N_MONTHS}  month'::interval) <= event.${DATE_COLUMN}
    AND event.${DATE_COLUMN} < insp.inspection_date
    WHERE p2e.dist_m <= ${MAX_DIST}
    AND insp.inspection_date BETWEEN '${MIN_INSP_DATE}' AND '${MAX_INSP_DATE}'
);
CREATE INDEX ON ${TABLE_NAME} (parcel_id, inspection_date);
CREATE INDEX ON ${TABLE_NAME} (id);

