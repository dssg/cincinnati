import logging
import logging.config
from feature_utils import make_inspections_address_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries

#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

def make_permits_features(con, n_months, max_dist):
    """
    Make permits features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """
    dataset = 'permits'
    date_column = 'issueddate'

    #Check that you have enough data to generate features,
    #the function will raise and Exception if you don't
    check_date_boundaries(con, n_months, dataset, date_column)

    make_inspections_address_nmonths_table(con, dataset, date_column,
                                                n_months=n_months,
                                                max_dist=max_dist,
                                                load=False)
    logger.info('Computing distance features for {}'.format(dataset))
    freq = group_and_count_from_db(con, dataset, n_months, max_dist)
    #Rename columns to avoid spaces and capital letters
    freq.columns = format_column_names(freq.columns)
    return freq
