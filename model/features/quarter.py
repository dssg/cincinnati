import pandas as pd

def make_quarter_features(con):

    query = """
        WITH t as (
        SELECT parcel_id, inspection_date,
              extract(month FROM inspection_date) as imonth
        FROM parcels_inspections
        ) SELECT
            parcel_id, inspection_date,
            CASE WHEN imonth in (1,2,3) THEN 1 ELSE 0 END AS first_quarter,
            CASE WHEN imonth in (4,5,6) THEN 1 ELSE 0 END AS second_quarter,
            CASE WHEN imonth in (7,8,9) THEN 1 ELSE 0 END AS third_quarter,
            CASE WHEN imonth in (10,11,12) THEN 1 ELSE 0 END AS fourth_quarter
        FROM t;
        """

    return pd.read_sql(query, con,  index_col=['parcel_id', 'inspection_date'] )
