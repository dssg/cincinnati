DROP TABLE IF EXISTS taxes_combined;

CREATE TABLE tax_combined AS(

    WITH t2007 AS (
        SELECT 2007 AS year,
        new_parcel_id AS parcel_id,
        CAST(mkt_total_val AS integer),
        CAST(mkt_impr_val AS integer),
        CAST(mkt_land_val AS integer)
        FROM taxes_2007
    ), t2008 AS (
        SELECT 2008 AS year,
        new_parcel_id AS parcel_id,
        CAST(mkt_total_val AS integer),
        CAST(mkt_impr_val AS integer),
        CAST(mkt_land_val AS integer)
        FROM taxes_2008
    ), t2009 AS (
        SELECT 2009 AS year,
        new_parcel_id AS parcel_id,
        CAST(mkt_total_val AS integer),
        CAST(mkt_impr_val AS integer),
        CAST(mkt_land_val AS integer)
        FROM taxes_2009
    ), t2010 AS (
        SELECT 2010 AS year,
        new_parcel_id AS parcel_id,
        CAST(mkt_total_val AS integer),
        CAST(mkt_impr_val AS integer),
        CAST(mkt_land_val AS integer)
        FROM taxes_2010
    ), t2011 AS (
        SELECT 2011 AS year,
        new_parcel_id AS parcel_id,
        CAST(mkt_total_val AS integer),
        CAST(mkt_impr_val AS integer),
        CAST(mkt_land_val AS integer)
        FROM taxes_2011
    ), t2012 AS (
        SELECT 2012 AS year,
        new_parcel_id AS parcel_id,
        CAST(mkt_total_val AS integer),
        CAST(mkt_impr_val AS integer),
        CAST(mkt_land_val AS integer)
        FROM taxes_2012
    ), t2013 AS (
        SELECT 2013 AS year,
        new_parcel_id AS parcel_id,
        CAST(mkt_total_val AS integer),
        CAST(mkt_impr_val AS integer),
        CAST(mkt_land_val AS integer)
        FROM taxes_2013
    ), t2014 AS (
        SELECT 2014 AS year,
        new_parcel_id AS parcel_id,
        CAST(mkt_total_val AS integer),
        CAST(mkt_impr_val AS integer),
        CAST(mkt_land_val AS integer)
        FROM taxes_2014
    ), t2015 AS (
        SELECT 2015 AS year,
        new_parcel_id AS parcel_id,
        CAST(mkt_total_val AS integer),
        CAST(mkt_impr_val AS integer),
        CAST(mkt_land_val AS integer)
        FROM taxes_2015
    )

    SELECT * FROM t2007
    UNION
    SELECT * FROM t2008
    UNION
    SELECT * FROM t2009
    UNION
    SELECT * FROM t2010
    UNION
    SELECT * FROM t2011
    UNION
    SELECT * FROM t2012
    UNION
    SELECT * FROM t2013
    UNION
    SELECT * FROM t2014
    UNION
    SELECT * FROM t2015
)