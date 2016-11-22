import logging
import logging.config
from feature_utils import make_inspections_latlong_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db, make_table_of_frequent_codes, \
        load_colpivot
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries
import pandas as pd

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

    # frequent service_codes, so we can prune them (there are too many)
    make_table_of_frequent_codes(con, col='service_code', intable='public.three11',
            outtable='public.frequentthree11_service_code', dropifexists=False)

    max_rnum = 15
    load_colpivot(con)
    cur = con.cursor()

    query = """
        DROP TABLE IF EXISTS three11features1_{n_months}months_{max_dist}m;
       
        DROP TABLE IF EXISTS joinedthree11_{n_months}months_{max_dist}m;

        -- join the inspections and three11
        CREATE TEMP TABLE joinedthree11_{n_months}months_{max_dist}m ON COMMIT DROP AS
            SELECT parcel_id, inspection_date,
                   agency_responsible,
                   status,
                   service_code,
                   CASE WHEN description='Request entered through the Web. Refer to Intake Questions for further description.'
                        THEN 1 ELSE 0 END AS webrequest
            FROM insp2three11_{n_months}months_{max_dist}m i2e
            LEFT JOIN LATERAL (
                SELECT * FROM public.three11 s where s.id=i2e.id
            ) event
            ON true
        ;
        CREATE INDEX ON joinedthree11_{n_months}months_{max_dist}m (parcel_id, inspection_date);
        
        -- make the simple features
        CREATE TEMP TABLE three11features1_{n_months}months_{max_dist}m ON COMMIT DROP AS
            SELECT 
                parcel_id,
                inspection_date,
                sum(webrequest) as sum_webrequest,
                avg(webrequest) as avg_webrequest,
                count(*) as total
            FROM joinedthree11_{n_months}months_{max_dist}m event
            GROUP BY parcel_id, inspection_date;
        CREATE INDEX ON three11features1_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- make the categorical (dummified) features 
        CREATE TEMP TABLE three11features2_{n_months}months_{max_dist}m ON COMMIT DROP AS
            -- restrict three11 levels to the {max_rnum} most common ones,
            -- using the tables of frequency counts for these levels that we created earlier
            SELECT parcel_id, inspection_date, 'service_code_'||coalesce(t.service_code,'missing') as categ, count(*) as count
            FROM joinedthree11_{n_months}months_{max_dist}m t
            LEFT JOIN public.frequentthree11_service_code freqcateg
            ON freqcateg.service_code = t.service_code
            WHERE freqcateg.rnum <= {max_rnum}
            GROUP BY parcel_id, inspection_date, t.service_code
        ;

        CREATE INDEX ON three11features2_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- Now call the pivot function to create columns with the 
        -- different fire types
        SELECT colpivot('three11pivot_{n_months}months_{max_dist}m',
                        'select * from three11features2_{n_months}months_{max_dist}m',
                        array['parcel_id','inspection_date'],
                        array['categ'],
                        'coalesce(#.count,0)',
                        null
        );
        CREATE INDEX ON three11pivot_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- still need to 'save' the tables into a permanent table
        DROP TABLE IF EXISTS three11features_{n_months}months_{max_dist}m;
        CREATE TABLE three11features_{n_months}months_{max_dist}m AS
            SELECT * FROM three11features1_{n_months}months_{max_dist}m
            JOIN three11pivot_{n_months}months_{max_dist}m
            USING (parcel_id, inspection_date)
        ;
    """.format(n_months=str(n_months), max_dist=str(max_dist),
                max_rnum = str(max_rnum))

    cur.execute(query)
    con.commit()
    
    # fetch the data
    query = """
        SELECT * FROM three11features_{n_months}months_{max_dist}m;
    """.format(n_months=str(n_months),
               max_dist=str(max_dist))

    df = pd.read_sql(query, con, index_col=['parcel_id', 'inspection_date'])

    # clean up the column names
    df.columns = map(lambda x: x.replace(' ','_').lower(), df.columns)
    df.columns = map(lambda x: ''.join(c for c in x if c.isalnum() or c=='_'),
                    df.columns)

    # drop the last interim table
    query = 'drop table three11features_{n_months}months_{max_dist}m'.format(
            n_months=str(n_months), max_dist=str(max_dist))
    cur.execute(query)
    con.commit()

    return df

