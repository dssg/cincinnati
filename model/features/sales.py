import logging
import logging.config
from feature_utils import make_inspections_address_nmonths_table, \
        compute_frequency_features, load_colpivot, format_column_names, \
        group_and_count_from_db, make_table_of_frequent_codes
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries
import itertools
import pandas as pd

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

    # there are several columns that we need to prune in terms of codes;
    # thus, make tables of value counts
    make_table_of_frequent_codes(con, col='use_code', intable='public.sales',
            outtable='public.frequentsales_use_codes', coalesceto="null", dropifexists=False)
    make_table_of_frequent_codes(con, col='instrument_type', intable='public.sales',
            outtable='public.frequentsales_instrument_types', dropifexists=False)
    make_table_of_frequent_codes(con, col='garage_type', intable='public.sales',
            outtable='public.frequentsales_garage_types', dropifexists=False)
    
    cur = con.cursor()

    # let's generate all the 'simple' features we might want;
    # each column will be named like 'avg_total_rooms'
    coltemplate = "{fun}({col}) AS {fun}_{col}"
    cols = [
        'number_of_parcels',
        'appraisal_area',
        'total_sales_records',
        'sale_price',
        'total_rooms',
        'full_bath',
        'half_bath',
        'fireplaces',
        'garage_capacity',
        'num_stories',
        'year_built',
        'finished_sq_ft',
        'total_finish_area',
        'first_floor_area',
        'half_floor_area',
        'finished_basement'
        ]
    funs = ['avg','sum','min','max','stddev']
    featureselects = ',\n'.join(coltemplate.format(fun=f,col=c) for f,c in itertools.product(funs, cols)) 

    # This is a template for a pivot table. In the sales table, we have several categorical columns.
    # We need to pivot these into columns, with counts grouped by parcel_id and inspection_date.
    # As a first step, we take make a table for each categorical column that we want to pivot.
    # Each such table has columns (parcel_id, inspection_date, categ, count), where categ is 
    # the level of our categorical column, and count is the number of times that level appears
    # for index (parcel_id, inspection_date). (We create a new level for 'null' rows.)
    # Here, we just define a template for this table query; we'll use it below.
    # {col} will be the categorical column name; joinedsales_Xmonths_Ym a join between sales and 
    # insp2sales_Xmonths_Ym.
    unionall_template = """
        SELECT parcel_id, inspection_date, '{col}_'||coalesce(t.{col},'missing') as categ, count(*) as count
        FROM joinedsales_{n_months}months_{max_dist}m t
        GROUP BY parcel_id, inspection_date, t.{col}
        """
    to_dummify_columns = ['style',
                          'grade',
                          'exterior_wall_type',
                          'basement',
                          'heating',
                          'air_conditioning']

    unionall_statements = '\n'.join([
                            'UNION ALL ( %s )'%unionall_template.format(col=col,
                                                                        n_months=str(n_months),
                                                                        max_dist=str(max_dist)
                                                                        )
                            for col in to_dummify_columns 
                            ])

    # this is the number of levels we'll restrict the pivoted use_code, instrument_type, and garage_type to
    max_rnum = 15 

    query = """
        DROP TABLE IF EXISTS salesfeatures1_{n_months}months_{max_dist}m;
       
        DROP TABLE IF EXISTS joinedsales_{n_months}months_{max_dist}m;

        -- join the inspections and sales
        CREATE TEMP TABLE joinedsales_{n_months}months_{max_dist}m ON COMMIT DROP AS
            SELECT parcel_id, inspection_date, event.* 
            FROM insp2sales_{n_months}months_{max_dist}m i2e
            LEFT JOIN LATERAL (
                SELECT * FROM public.sales s where s.id=i2e.id
            ) event
            ON true
        ;
        CREATE INDEX ON joinedsales_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- make the simple features
        CREATE TEMP TABLE salesfeatures1_{n_months}months_{max_dist}m ON COMMIT DROP AS
            SELECT 
                parcel_id,
                inspection_date,
                count(*) as total,
                {featureselects}
            FROM joinedsales_{n_months}months_{max_dist}m event
            GROUP BY parcel_id, inspection_date;
        CREATE INDEX ON salesfeatures1_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- make the categorical (dummified) features 
        CREATE TEMP TABLE salesfeatures2_{n_months}months_{max_dist}m ON COMMIT DROP AS
        
        -- now, we have a few columns with too many levels; we restrict these levels to the {max_rnum} most common ones,
        -- using the tables of frequency counts for these levels that we created earlier
        SELECT parcel_id, inspection_date, 'use_code_'||coalesce(t.use_code::varchar,'missing') as categ, count(*) as count
        FROM joinedsales_{n_months}months_{max_dist}m t
        LEFT JOIN public.frequentsales_use_codes freqcateg
        ON freqcateg.use_code = t.use_code
        WHERE freqcateg.rnum <= {max_rnum}
        GROUP BY parcel_id, inspection_date, t.use_code
        UNION ALL (
          SELECT parcel_id, inspection_date, 'instrument_type_'||coalesce(t.instrument_type,'missing') as categ, count(*) as count
          FROM joinedsales_{n_months}months_{max_dist}m t
          LEFT JOIN public.frequentsales_instrument_types freqcateg
          ON freqcateg.instrument_type = t.instrument_type
          WHERE freqcateg.rnum <= {max_rnum}
          GROUP BY parcel_id, inspection_date, t.instrument_type
        )
        UNION ALL (
          SELECT parcel_id, inspection_date, 'garage_type_'||coalesce(t.garage_type,'missing') as categ, count(*) as count
          FROM joinedsales_{n_months}months_{max_dist}m t
          LEFT JOIN public.frequentsales_garage_types freqcateg
          ON freqcateg.garage_type = t.garage_type
          WHERE freqcateg.rnum <= {max_rnum}
          GROUP BY parcel_id, inspection_date, t.garage_type
        )
        {unionall_statements} -- these are all the columns that we defined above
        ;
        
        CREATE INDEX ON salesfeatures2_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- Now call the pivot function to create columns with the 
        -- different fire types
        SELECT colpivot('salespivot_{n_months}months_{max_dist}m',
                        'select * from salesfeatures2_{n_months}months_{max_dist}m',
                        array['parcel_id','inspection_date'],
                        array['categ'],
                        'coalesce(#.count,0)',
                        null
        );
        CREATE INDEX ON salespivot_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- still need to 'save' the tables into a permanent table
        DROP TABLE IF EXISTS salesfeatures_{n_months}months_{max_dist}m;
        CREATE TABLE salesfeatures_{n_months}months_{max_dist}m AS
            SELECT * FROM salesfeatures1_{n_months}months_{max_dist}m
            JOIN salespivot_{n_months}months_{max_dist}m
            USING (parcel_id, inspection_date)
        ;
    """.format(n_months=str(n_months), max_dist=str(max_dist),
                featureselects=featureselects,
                unionall_statements=unionall_statements,
                max_rnum = str(max_rnum))

    cur.execute(query)
    con.commit()
    
    # fetch the data
    query = """
        SELECT * FROM salesfeatures_{n_months}months_{max_dist}m;
    """.format(n_months=str(n_months),
               max_dist=str(max_dist))

    df = pd.read_sql(query, con, index_col=['parcel_id', 'inspection_date'])

    # clean up the column names
    df.columns = map(lambda x: x.replace(' ','_').lower(), df.columns)
    df.columns = map(lambda x: ''.join(c for c in x if c.isalnum() or c=='_'),
                    df.columns)

    # drop the last interim table
    query = 'drop table salesfeatures_{n_months}months_{max_dist}m'.format(
            n_months=str(n_months), max_dist=str(max_dist))
    cur.execute(query)
    con.commit()

    return df

