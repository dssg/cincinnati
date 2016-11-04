--Join parcel column in each inspection in
--parcels_inspection (in whatever it is the current schema)
--with addresses that are within 1Km (using parcel2address table)
--then filter those addreses for events within 3 month of
--inspection date

--This script is intended to be used as a template for various tables
CREATE TABLE ${TABLE_NAME} AS (
    --schema is not specified here
	--since the db connection should set one
	--using SET SCHEMA
    SELECT
        insp.parcel_id,
        insp.inspection_date,
        ST_Distance(parcels.geom, address.geom)/3.281 AS dist_m,
        event.id --columns to select from event
    FROM parcels_inspections AS insp
    JOIN shape_files.parcels_cincy AS parcels ON (insp.parcel_id = parcels.parcelid)
    JOIN public.address AS address ON (ST_DWithin(parcels.geom, address.geom, ${MAX_DIST}*3.281::double precision))
    JOIN public.${DATASET} AS event ON (
        address.id=event.address_id
        AND (insp.inspection_date - '${N_MONTHS} month'::interval) <= event.${DATE_COLUMN}
        AND event.${DATE_COLUMN} <= insp.inspection_date
    )
    WHERE insp.inspection_date BETWEEN '${MIN_INSP_DATE}' AND '${MAX_INSP_DATE}'
);

