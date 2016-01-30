--Join parcel column in eac inspection in
--parcels_inspection (in whatever it is the current schema)
--with events that are within X Km (using parcel2TABLE table)
--then filter those addreses for events within 3 month of
--inspection date

--This script is intended to be used as a template for various tables
--Example for three11
SELECT insp.parcel_id, insp.inspection_date, p2e.dist_km, event.*
FROM features.parcels_inspections AS insp
JOIN parcel2three11 AS p2e
USING (parcel_id)
JOIN three11 AS event
ON three11_id=event.id
AND (insp.inspection_date - '3 month'::interval) <= event.requested_datetime
AND event.requested_datetime <= insp.inspection_date
LIMIT 100;