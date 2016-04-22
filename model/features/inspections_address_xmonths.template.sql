--Join parcel column in eac inspection in
--parcels_inspection (in whatever it is the current schema)
--with addresses that are within 1Km (using parcel2address table)
--then filter those addreses for events within 3 month of
--inspection date

--This script is intended to be used as a template for various tables
CREATE TABLE ${TABLE_NAME} AS (
    WITH inspections_subset AS(
        SELECT * FROM features.parcels_inspections
        WHERE '${MIN_INSP_DATE}' <= inspection_date
        AND inspection_date <= '${MAX_INSP_DATE}'
    )

    SELECT
        insp.parcel_id, insp.inspection_date,
        p2a.dist_m,
        event.id --columns to select from event
    FROM inspections_subset AS insp
    JOIN public.parcel2address AS p2a
    USING (parcel_id)
    JOIN public.address
    ON address_id=address.id
    JOIN public.${DATASET} AS event
    ON address.id=event.address_id
    AND (insp.inspection_date - '${N_MONTHS} month'::interval) <= event.${DATE_COLUMN}
    AND event.${DATE_COLUMN} <= insp.inspection_date
);

