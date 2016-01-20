--Generate a view with the parcel, complain date, distance
--and some columns to generate features
CREATE VIEW public.parcels_three11_view AS (
    SELECT p2t11.parcelid, t11.requested_datetime, p2t11.dist_km,
       t11.service_code, t11.agency_responsible
    FROM public.parcels_to_three11 AS p2t11
    JOIN public.three11 AS t11
    USING (service_request_id)
)
