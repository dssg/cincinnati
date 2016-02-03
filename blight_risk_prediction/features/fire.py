import logging
import logging.config
from feature_utils import load_inspections_address_nmonths_table, compute_frequency_features
from feature_utils import format_column_names
from dstools.config import load
#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger(__name__)

def make_fire_features(con):
    """
    Make Fire features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """
    dataset = 'fire'
    date_column = 'date'
    n_months = 3

    #Load data with events that happened before x months of inspection database
    df = load_inspections_address_nmonths_table(con, dataset, date_column,
                                                n_months=n_months)
    #Use the recently created table to compute features.
    #Group rows by parcel_id and inspection_date
    #For now, just perform counts on the categorical variables
    #More complex features could combine the distance value
    #as well as interacting features
    logger.info('Computing distance features for {}'.format(table_name))
    freq = compute_frequency_features(df, columns='signal')
    #Rename columns to avoid spaces and capital letters
    freq.columns = format_column_names(freq.columns, prefix=dataset)
    return freq
