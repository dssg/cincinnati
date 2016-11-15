import logging
import logging.config
from feature_utils import make_inspections_address_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db, load_colpivot
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries
from psycopg2 import ProgrammingError, InternalError
import pandas as pd

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

    load_colpivot(con)

    #Get the time window for which you can generate features
    min_insp, max_insp = check_date_boundaries(con, n_months, dataset, date_column)

    make_inspections_address_nmonths_table(con, dataset, date_column,
        min_insp, max_insp, n_months=n_months, max_dist=max_dist, load=False)
    
    logger.info('Computing distance features for {}'.format(dataset))

    cur = con.cursor()

    insp2tablename = ('insp2{dataset}_{n_months}months'
                  '_{max_dist}m').format(dataset='permits',
                                         n_months=str(n_months),
                                         max_dist=str(max_dist))

    # create a table of the most common proposeduse types,
    # so we can limit the pivot later to the 15 most common
    # types of uses
    query = """
        CREATE TABLE public.frequentpermituses AS (
        WITH t as (
        SELECT proposeduse, count(*) AS count
        FROM public.permits
        GROUP BY proposeduse
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
        logger.warning("CONTINUING, NOT RE-RUNNING frequentpermituses table QUERY.....")
        cur.close()
        cur = con.cursor()

    con.commit()
    cur.close()
    cur = con.cursor()
    query = """
        DROP TABLE IF EXISTS permitfeatures1_{n_months}months_{max_dist}m;

        CREATE TEMP TABLE permitfeatures1_{n_months}months_{max_dist}m ON COMMIT DROP AS
            SELECT 
                parcel_id,
                inspection_date,
                count(*) as total,
                avg(completeddate-applieddate) as avg_days_applied_to_completed,
                avg(completeddate-issueddate) as avg_days_issued_to_completed,
                avg(issueddate-applieddate) as avg_days_applied_to_issued,
                avg(expiresdate-issueddate) as avg_days_issued_to_expires,
                avg(expiresdate-completeddate) as avg_days_completed_to_expires,
                avg(CASE WHEN issueddate IS NOT NULL THEN 1 ELSE 0 END) as avg_issued,
                avg(CASE WHEN completeddate IS NOT NULL THEN 1 ELSE 0 END) as avg_completed,
                avg(CASE WHEN expiresdate IS NOT NULL THEN 1 ELSE 0 END) as avg_expires,
                avg(totalsqft) as avg_sqft,
                avg(estprojectcostdec) as avg_estcost,
                avg(units) as avg_units,
                avg(CASE WHEN coissueddate IS NOT NULL THEN 1 ELSE 0 END) as avg_is_coissued,
                avg(substring(fee from 2)::real) as avg_fee,
                avg(CASE WHEN companyname='OWNER' THEN 1 ELSE 0 END) as avg_owner_is_company
            FROM insp2permits_{n_months}months_{max_dist}m i2e
            LEFT JOIN public.permits event USING (id)
            GROUP BY parcel_id, inspection_date;

        -- Join the permits with the inspections; then concatenate the 
        -- inspections and the various categorical variables (we'll pivot later)
        CREATE TEMP TABLE permitfeatures2_{n_months}months_{max_dist}m ON COMMIT DROP AS
        WITH t as ( 
            SELECT * FROM insp2permits_{n_months}months_{max_dist}m i2e
            LEFT JOIN public.permits event USING (id)
        ) 
        SELECT parcel_id, inspection_date, 'permitclass_'||coalesce(permitclass,'missing') as categ, count(*) as count
          FROM t GROUP BY parcel_id, inspection_date, permitclass
        UNION ALL (
          SELECT parcel_id, inspection_date, 'currstatus_'||coalesce(statuscurrent,'missing') as categ, count(*) as count
          FROM t GROUP BY parcel_id, inspection_date, statuscurrent
        )
        UNION ALL (
          SELECT parcel_id, inspection_date, 'workclass_'||coalesce(workclass,'missing') as categ, count(*) as count
          FROM t GROUP BY parcel_id, inspection_date, workclass
        )
        UNION ALL (
          SELECT parcel_id, inspection_date, 'permittype_'||coalesce(permittype,'missing') as categ, count(*) as count
          FROM t GROUP BY parcel_id, inspection_date, permittype
        )
        UNION ALL (
          SELECT parcel_id, inspection_date, 'prpsduse_'||coalesce(t.proposeduse,'missing') as categ, count(*) as count
          FROM t
          LEFT JOIN public.frequentpermituses frequse
          ON frequse.proposeduse = t.proposeduse
          WHERE frequse.rnum <= 15
          GROUP BY parcel_id, inspection_date, t.proposeduse
        );

        -- Now call the pivot function to create columns with the 
        -- different fire types
        SELECT colpivot('permitpivot_{n_months}months_{max_dist}m',
                        'select * from permitfeatures2_{n_months}months_{max_dist}m',
                        array['parcel_id','inspection_date'],
                        array['categ'],
                        'coalesce(#.count,0)',
                        null
        );

        -- still need to 'save' the tables into a permanent table
        CREATE TABLE permitfeatures_{n_months}months_{max_dist}m AS
            SELECT * FROM permitfeatures1_{n_months}months_{max_dist}m
            JOIN permitpivot_{n_months}months_{max_dist}m
            USING (parcel_id, inspection_date)
        ;
    """.format(n_months=str(n_months), max_dist=str(max_dist))

    cur.execute(query)
    con.commit()
    
    # fetch the data
    query = """
        SELECT * FROM permitfeatures_{n_months}months_{max_dist}m;
    """.format(n_months=str(n_months),
               max_dist=str(max_dist))

    df = pd.read_sql(query, con, index_col=['parcel_id', 'inspection_date'])

    # clean up the column names
    df.columns = map(lambda x: x.replace(' ','_').lower(), df.columns)
    df.columns = map(lambda x: ''.join(c for c in x if c.isalnum() or c=='_'),
                    df.columns)

    # drop the last interim table
    query = 'drop table permitfeatures_{n_months}months_{max_dist}m'.format(
            n_months=str(n_months), max_dist=str(max_dist))
    cur.execute(query)
    con.commit()

    return df

