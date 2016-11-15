import logging
import logging.config
from feature_utils import make_inspections_address_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries
import os
from psycopg2 import ProgrammingError, InternalError
import pandas as pd

#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

def make_fire_features(con, n_months, max_dist):
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
    date_column = 'incident_date'

    #Get the time window for which you can generate features
    min_insp, max_insp = check_date_boundaries(con, n_months, dataset, date_column)

    make_inspections_address_nmonths_table(con, dataset, date_column,
        min_insp, max_insp, n_months=n_months, max_dist=max_dist, load=False)
    
    logger.info('Computing distance features for {}'.format(dataset))

    insp2tablename = ('insp2{dataset}_{n_months}months'
                  '_{max_dist}m').format(dataset='fire',
                                         n_months=str(n_months),
                                         max_dist=str(max_dist))

    # add the colpivot function to our Postgres schema
    with open(os.path.join(os.environ['ROOT_FOLDER'], 
                'model','features', 'colpivot.sql'), 'r') as fin:
        query = fin.read()

    cur = con.cursor()
    cur.execute(query)
    con.commit()

    # create a table of the most common fire types,
    # so we can limit the pivot later to the 15 most common
    # types of incidents
    query = """
        CREATE TABLE public.frequentfiretypes AS (
        WITH t as (
        SELECT incident_type_id, incident_type_desc, count(*) AS count
        FROM public.fire
        GROUP BY incident_type_id, incident_type_desc
        ORDER BY count desc
        )
        SELECT row_number() OVER () as rnum, t.*
        FROM t
        );
    """

    # if it already exists, no need to re-run; we're using all 
    # the data to find the most common types anyway
    try:
        cur.execute(query)
        con.commit()
    except ProgrammingError as e:
        logger.warning("Catching Exception: " + e.message)
        logger.warning("CONTINUING, NOT RE-RUNNING frequentfiretypes table QUERY.....")
        cur.close()
        cur = con.cursor()

    # let's make an index on that little table
    query = """
        CREATE INDEX frequentfiretype_idx ON public.frequentfiretypes (incident_type_id);
    """
    # if the index already exists, we don't re-run
    try:
        cur.execute(query)
        con.commit()
    except (InternalError, ProgrammingError) as e:
        logger.warning("Catching Exception: " + e.message)
        logger.warning("CONTINUING, NOT RE-RUNNING frequentfiretype_idx QUERY.....")
        cur.close()
        cur = con.cursor()

    # also make sure that the fire data has an index there, as we want to join on it
    query = """
        CREATE INDEX firetype_idx ON public.fire (incident_type_id);
    """
    try:
        cur.execute(query)
        con.commit()
    except (InternalError, ProgrammingError) as e:
        logger.warning("Catching Exception: " + e.message)
        logger.warning("CONTINUING, NOT RE-RUNNING firetype_idx QUERY.....")
        cur.close()
        cur = con.cursor()

    # now on to the actual feature generation
    con.commit()
    cur.close()
    cur = con.cursor()
    query = """

         --begin;

        DROP TABLE IF EXISTS firefeatures_{n_months}months_{max_dist}m;

        -- Join the fire with the inspections; then group by 
        -- inspections and fire types (we'll pivot later)
        CREATE TEMP TABLE firetypes_{n_months}months_{max_dist}m ON COMMIT DROP AS (
            SELECT parcel_id, inspection_date, event.incident_type_desc,
            count(*) as count
            FROM insp2fire_{n_months}months_{max_dist}m i2e
            LEFT JOIN public.fire event USING (id)
            LEFT JOIN public.frequentfiretypes frequentfires 
            ON frequentfires.incident_type_id = event.incident_type_id
            WHERE frequentfires.rnum <= 15
            GROUP BY parcel_id, inspection_date, event.incident_type_desc
        );

        -- Now call the pivot function to create columns with the 
        -- different fire types
        SELECT colpivot('firefeatures_{n_months}months_{max_dist}m',
                        'select * from firetypes_{n_months}months_{max_dist}m',
                        array['parcel_id','inspection_date'],
                        array['incident_type_desc'],
                        'coalesce(#.count,0)',
                        null
        );

        -- The pivot function only creates a temp table,
        -- so we still need to save it into a proper table.
        -- Also, this is a good time to join in the other 
        -- features we want.

        DROP TABLE IF EXISTS firefeatures2_{n_months}months_{max_dist}m;

        CREATE TEMP TABLE firefeatures2_{n_months}months_{max_dist}m AS (
            SELECT parcel_id, inspection_date,
                count(*) as total, -- note that total includes the non-frequent incident types
                avg(
                   extract(epoch from event.unit_clear_date_time-event.alarm_date_time)::int/60
                ) as avg_clear_time_minutes
            FROM insp2fire_{n_months}months_{max_dist}m i2e
            LEFT JOIN public.fire event USING (id)
            GROUP BY parcel_id, inspection_date
        ); 

        CREATE TABLE firefeatures_{n_months}months_{max_dist}m AS
            SELECT * FROM firefeatures_{n_months}months_{max_dist}m
            JOIN firefeatures2_{n_months}months_{max_dist}m
            USING (parcel_id, inspection_date)
        ;

         --commit;

        """.format(insp2tablename=insp2tablename,
                   n_months=str(n_months),
                   max_dist=str(max_dist))

    cur.execute(query)
    con.commit()

    query = """
        SELECT * FROM firefeatures_{n_months}months_{max_dist}m;
    """.format(n_months=str(n_months),
               max_dist=str(max_dist))

    # fetch the data
    df = pd.read_sql(query, con, index_col=['parcel_id', 'inspection_date'])

    # clean up the column names
    df.columns = map(lambda x: x.replace(' ','_').lower(), df.columns)
    df.columns = map(lambda x: ''.join(c for c in x if c.isalnum() or c=='_'),
                    df.columns)

    # drop the last interim table
    query = 'drop table firefeatures_{n_months}months_{max_dist}m'.format(
            n_months=str(n_months), max_dist=str(max_dist))
    cur.execute(query)
    con.commit()

    return df

