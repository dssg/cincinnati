ALTER TABLE public.taxes_2007
ADD COLUMN new_parcel_id text;

UPDATE public.taxes_2007
SET new_parcel_id = '0' || lpad(public.taxes_2007.parcel_id, 11);

ALTER TABLE public.taxes_2008
ADD COLUMN new_parcel_id text;

UPDATE public.taxes_2008
SET new_parcel_id = '0' || lpad(public.taxes_2008.parcel_id, 11);

ALTER TABLE public.taxes_2009
ADD COLUMN new_parcel_id text;

UPDATE public.taxes_2009
SET new_parcel_id = '0' || lpad(public.taxes_2009.parcel_id, 11);

ALTER TABLE public.taxes_2010
ADD COLUMN new_parcel_id text;

UPDATE public.taxes_2010
SET new_parcel_id = '0' || lpad(public.taxes_2010.parcel_id, 11);

ALTER TABLE public.taxes_2011
ADD COLUMN new_parcel_id text;

UPDATE public.taxes_2011
SET new_parcel_id = '0' || lpad(public.taxes_2011.parcel_id, 11);

ALTER TABLE public.taxes_2012
ADD COLUMN new_parcel_id text;

UPDATE public.taxes_2012
SET new_parcel_id = '0' || lpad(public.taxes_2012.parcel_id, 11);

ALTER TABLE public.taxes_2013
ADD COLUMN new_parcel_id text;

UPDATE public.taxes_2013
SET new_parcel_id = '0' || lpad(public.taxes_2013.parcel_id, 11);

ALTER TABLE public.taxes_2014
ADD COLUMN new_parcel_id text;

UPDATE public.taxes_2014
SET new_parcel_id = '0' || lpad(public.taxes_2014.parcel_id, 11);

ALTER TABLE public.taxes_2015
ADD COLUMN new_parcel_id text;

UPDATE public.taxes_2015
SET new_parcel_id = '0' || lpad(public.taxes_2015.property_number, 11);

--Note: the code below no longer works since the ETL is detecting forcl_flag
--as boolean instead of string

--UPDATE public.taxes_2015
--SET forcl_flag = replace(forcl_flag, 'Yes', 'Y');

--UPDATE public.taxes_2015
--SET forcl_flag = replace(forcl_flag, 'No', 'N');
