import logging
import logging.config
from feature_utils import make_inspections_address_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries
import pandas as pd

#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

def make_crime_features(con, n_months, max_dist):
    """
    Make crime features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """
    dataset = 'crime'
    date_column = 'occurred_on'

    #Get the time window for which you can generate features
    min_insp, max_insp = check_date_boundaries(con, n_months, dataset, date_column)

    make_inspections_address_nmonths_table(con, dataset, date_column,
        min_insp, max_insp, n_months=n_months, max_dist=max_dist, load=False)

    logger.info('Computing distance features for {}'.format(dataset))

    max_rnum = 15

    # make a table of the more general offense frequencies so we can prune them
    # also include a column with an array of corresponding detailed levels
    query = """
        DROP TABLE IF EXISTS public.frequentcrimes_orc;
        CREATE TABLE public.frequentcrimes_orc AS (
        WITH t as (
        SELECT substring(orc from ' \((\w*)\) ') as orc_combined,
               array_agg(distinct orc) as all_orcs,
               count(*) as count
        FROM public.crime
        GROUP BY orc_combined
        ORDER BY count desc
        )
        SELECT 
            row_number() OVER () as rnum,
            t.orc_combined,
            t.all_orcs,
            CASE WHEN row_number() OVER () <= {rnum} THEN t.orc_combined
            ELSE 'other' END AS level
        FROM t
        );""".format(rnum=max_rnum)

    cur = con.cursor()
    cur.execute(query)
    con.commit()

    query = """
        DROP TABLE IF EXISTS crimefeatures1_{n_months}months_{max_dist}m;
       
        DROP TABLE IF EXISTS joinedcrime_{n_months}months_{max_dist}m;

        -- join the inspections and crime
        CREATE TEMP TABLE joinedcrime_{n_months}months_{max_dist}m ON COMMIT DROP AS
            SELECT parcel_id, inspection_date,
                   substring(event.orc from ' \((\w*)\) ') as orc_combined
            FROM insp2crime_{n_months}months_{max_dist}m i2e
            LEFT JOIN LATERAL (
                SELECT * FROM public.crime s where s.id=i2e.id
            ) event
            ON true
        ;
        CREATE INDEX ON joinedcrime_{n_months}months_{max_dist}m (parcel_id, inspection_date);
        
        -- make the simple features
        CREATE TEMP TABLE crimefeatures1_{n_months}months_{max_dist}m ON COMMIT DROP AS
            SELECT 
                parcel_id,
                inspection_date,
                count(*) as total
            FROM joinedcrime_{n_months}months_{max_dist}m event
            GROUP BY parcel_id, inspection_date;
        CREATE INDEX ON crimefeatures1_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- make the categorical (dummified) features 
        CREATE TEMP TABLE crimefeatures2_{n_months}months_{max_dist}m ON COMMIT DROP AS

            -- restrict crime levels to the 15 most common ones,
            -- using the tables of frequency counts for these levels that we created earlier
            -- also make sure all 15 levels appear

            SELECT 
                t2.parcel_id, t2.inspection_date,
                'orc_combined_'||t2.level AS categ,
                coalesce(t1.count,0) as count   
             FROM
             (SELECT parcel_id, inspection_date,
                     ft.level,
                     count(*) as count
              FROM joinedcrime_{n_months}months_{max_dist}m event
              LEFT JOIN public.frequentcrimes_orc ft
              ON ft.orc_combined = event.orc_combined
              GROUP BY parcel_id, inspection_date, ft.level
             ) t1
             RIGHT JOIN
             (SELECT parcel_id, inspection_date, ft.level 
                 FROM parcels_inspections
                 JOIN 
                     (select distinct level from public.frequentcrimes_orc) ft
                 ON true
             ) t2
             USING (parcel_id, inspection_date,level)
        ;

        CREATE INDEX ON crimefeatures2_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- Now call the pivot function to create columns with the 
        -- different fire types
        SELECT colpivot('crimepivot_{n_months}months_{max_dist}m',
                        'select * from crimefeatures2_{n_months}months_{max_dist}m',
                        array['parcel_id','inspection_date'],
                        array['categ'],
                        'coalesce(#.count,0)',
                        null
        );
        CREATE INDEX ON crimepivot_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- still need to 'save' the tables into a permanent table
        DROP TABLE IF EXISTS crimefeatures_{n_months}months_{max_dist}m;
        CREATE TABLE crimefeatures_{n_months}months_{max_dist}m AS
            SELECT * FROM crimefeatures1_{n_months}months_{max_dist}m
            JOIN crimepivot_{n_months}months_{max_dist}m
            USING (parcel_id, inspection_date)
        ;
    """.format(n_months=str(n_months), max_dist=str(max_dist))

    cur.execute(query)
    con.commit()
    
    # fetch the data
    query = """
        SELECT * FROM crimefeatures_{n_months}months_{max_dist}m;
    """.format(n_months=str(n_months),
               max_dist=str(max_dist))

    df = pd.read_sql(query, con, index_col=['parcel_id', 'inspection_date'])

    # clean up the column names
    df.columns = map(lambda x: x.replace(' ','_').lower(), df.columns)
    df.columns = map(lambda x: ''.join(c for c in x if c.isalnum() or c=='_'),
                    df.columns)

    # drop the last interim table
    query = 'drop table crimefeatures_{n_months}months_{max_dist}m'.format(
            n_months=str(n_months), max_dist=str(max_dist))
    cur.execute(query)
    con.commit()

    return df

