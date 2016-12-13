CREATE TABLE public.weather AS
SELECT make_timestamp(year, month::int, day::int, hour::int, 0, 0) as date,
       w.*
FROM public.weather_tmp w;
CREATE INDEX ON public.weather (date);
