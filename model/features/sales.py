import logging
import logging.config
from feature_utils import make_inspections_address_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db, make_table_of_frequent_codes
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries

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
    date_column = 'date_of_sale'

    load_colpivot(con)

    #Get the time window for which you can generate features
    min_insp, max_insp = check_date_boundaries(con, n_months, dataset, date_column)

    make_inspections_address_nmonths_table(con, dataset, date_column,
        min_insp, max_insp, n_months=n_months, max_dist=max_dist, load=False)
    
    logger.info('Computing distance features for {}'.format(dataset))

    cur = con.cursor()

    insp2tablename = ('insp2{dataset}_{n_months}months'
                  '_{max_dist}m').format(dataset='sales',
                                         n_months=str(n_months),
                                         max_dist=str(max_dist))

    # freq = group_and_count_from_db(con, dataset, n_months, max_dist)
    # #Rename columns to avoid spaces and capital letters
    # freq.columns = format_column_names(freq.columns)
    # return freq
