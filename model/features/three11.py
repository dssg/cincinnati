import logging
import logging.config
from feature_utils import make_inspections_latlong_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries

#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

def make_three11_features(con, n_months, max_dist):
    """
    Make three11 features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """
    dataset = 'three11'
    date_column = 'requested_datetime'

    #Get the time window for which you can generate features
    min_insp, max_insp = check_date_boundaries(con, n_months, dataset, date_column)

    make_inspections_latlong_nmonths_table(con, dataset, date_column,
        min_insp, max_insp, n_months=n_months, max_dist=max_dist, load=False)


    logger.info('Computing distance features for {}'.format(dataset))
    freq = group_and_count_from_db(con, dataset, n_months, max_dist)
    #Rename columns to avoid spaces and capital letters
    freq.columns = format_column_names(freq.columns)
    return freq
