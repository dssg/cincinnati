ALTER TABLE public.bld_info
ADD COLUMN parcel_id text;

UPDATE public.bld_info 
SET parcel_id = '0' || lpad(public.bld_info.mapblolot, 11);
