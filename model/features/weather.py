from lib_cinci.features import tables_in_schema
import logging
import logging.config
from feature_utils import make_inspections_latlong_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db, make_table_of_frequent_codes
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries
import pandas as pd

#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

def make_weather_features(con):
    """
    Make weather features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """
    logging.info("Making weather features")

    query = """
        SELECT insp.parcel_id, t.*
        FROM parcels_inspections insp
        LEFT JOIN
        (SELECT inspection_date,
                avg(air_temp) as avg_air_temp,
                avg(wind_speed_rate) as avg_wind_speed_rate,
                avg(sea_level_pressure) as avg_sea_level_pressure,
                avg(liquid_precipitation_depth_dimension_one_hour) as avg_precipitation
            FROM (select distinct inspection_date from parcels_inspections) pinsp
            JOIN public.weather w
            ON w.date < inspection_date
            AND w.date >= (inspection_date - '6 weeks'::interval)
            GROUP BY inspection_date
        ) t
        USING (inspection_date); 
        """
    
    # fetch the data
    df = pd.read_sql(query, con, index_col=['parcel_id', 'inspection_date'])

    # clean up the column names
    df.columns = map(lambda x: x.replace(' ','_').lower(), df.columns)
    df.columns = map(lambda x: ''.join(c for c in x if c.isalnum() or c=='_'),
                    df.columns)

    return df


