import pandas as pd

def make_quarter_features(con):

    query = """
        SELECT parcel_id, inspection_date,
              ((extract(month FROM inspection_date)-1)::int/3) + 1 AS quarter
        FROM parcels_inspections;
        """

    return pd.read_sql(query, con,  index_col=['parcel_id', 'inspection_date'] )
