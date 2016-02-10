import logging
import logging.config
from feature_utils import load_inspections_address_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db
from dstools.config import load
#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

def make_sales_features(con, n_months, max_dist):
    """
    Make sales features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """
    dataset = 'sales'
    date_column = 'datesale'

    #Load data with events that happened before x months of inspection database
    #df = load_inspections_address_nmonths_table(con, dataset, date_column,
    #                                            n_months=n_months,
    #                                            max_dist=max_dist)
    #Use the recently created table to compute features.
    #Group rows by parcel_id and inspection_date
    #For now, just perform counts on the categorical variables
    #More complex features could combine the distance value
    #as well as interacting features
    logger.info('Computing distance features for {}'.format(dataset))
    #freq = compute_frequency_features(df, columns='usecode')
    freq = group_and_count_from_db(con, dataset, n_months, max_dist)
    #Rename columns to avoid spaces and capital letters
    freq.columns = format_column_names(freq.columns)
    return freq