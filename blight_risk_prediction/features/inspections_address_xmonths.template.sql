--Join parcel column in eac inspection in
--parcels_inspection (in whatever it is the current schema)
--with addresses that are within 1Km (using parcel2address table)
--then filter those addreses for events within 3 month of
--inspection date

--This script is intended to be used as a template for various tables
CREATE TABLE insp_$N_MONTHSmonths_$TABLE_NAME AS (
    SELECT
        insp.parcel_id, insp.inspection_date,
        p2a.dist_km,
        $TABLE_NAME.*
    FROM parcels_inspections AS insp
    JOIN public.parcel2address AS p2a
    USING (parcel_id)
    JOIN public.address
    ON address_id=address.id
    JOIN public.$TABLE_NAME
    ON address.id=$TABLE_NAME.address_id
    AND (insp.inspection_date - '$N_MONTHS month'::interval) <= $TABLE_NAME.$DATE_COLUMN
    AND $TABLE_NAME.$DATE_COLUMN <= insp.inspection_date
);

