import logging
import logging.config
from feature_utils import load_inspections_latlong_nmonths_table, compute_frequency_features
from feature_utils import format_column_names
from dstools.config import load
#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

def make_permits_features(con, n_months):
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

    #Load data with events that happened before x months of inspection database
    df = load_inspections_latlong_nmonths_table(con, dataset, date_column,
                                                n_months=n_months)
    #Use the recently created table to compute features.
    #Group rows by parcel_id and inspection_date
    #For now, just perform counts on the categorical variables
    #More complex features could combine the distance value
    #as well as interacting features
    logger.info('Computing distance features for {}'.format(dataset))
    freq = compute_frequency_features(df, columns='description')
    #Rename columns to avoid spaces and capital letters
    freq.columns = format_column_names(freq.columns)
    return freq
