from feature_utils import create_inspections_address_xmonts_table, compute_frequency_features

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
    #Save current schema, this is important because if some of the queries
    #fail, you need to do a rollback, which will reset the previously set schema
    cur = con.cursor()
    cur.execute('SELECT current_schema;')
    schema = cur.fetchone()[0]

    table_name = 'fire'
    date_column = 'date'
    n_months = 3

    #Create table with events that happened before x months of inspection database
    #If table exists, send message and skip
    create_inspections_address_xmonths_table(con, schema,
                                            table_name,
                                            date_column,
                                            n_months=n_months)

    #Use the recently created table to compute features.
    #Group rows by parcel_id and inspection_date
    #For now, just perform counts on the categorical variables
    #More complex features could combine the distance value
    #as well as interacting features
    table_name = 'insp_{}months_{}'.format(n_months, table_name)
    df = compute_frequency_features_from_table(con, table_name, columns='signal')
    return df
