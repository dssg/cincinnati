from lib_cinci.features import tables_in_schema
import logging
import logging.config
from feature_utils import make_inspections_latlong_nmonths_table, compute_frequency_features
from feature_utils import format_column_names, group_and_count_from_db
from lib_cinci.config import load
from lib_cinci.features import check_date_boundaries
import pandas as pd

#Config logger
logging.config.dictConfig(load('logger_config.yaml'))
logger = logging.getLogger()

def make_inspections_features(con, n_months, max_dist):
    """
    Make inspections features

    Input:
    db_connection: connection to postgres database.
                   "set schema ..." must have been called on this connection
                   to select the correct schema from which to load inspections

    Output:
    A pandas dataframe, with one row per inspection and one column per feature.
    """
    dataset = 'inspections_views.events_parcel_id'
    date_column = 'date'

    ## ------------------------------------------------------------------------
    ## Make the parcel_id-to-nearby-houses table, if it's not there yet.
    ## ------------------------------------------------------------------------

    query = """
        CREATE TABLE insp2houses_{max_dist}m AS
            SELECT  
                feature_y.parcel_id,
                count(*) as parcels
            FROM (
                SELECT t.parcel_id,
                       p.geom
                FROM (SELECT DISTINCT parcel_id FROM parcels_inspections) t
                LEFT JOIN shape_files.parcels_cincy p
                ON t.parcel_id=p.parcelid
            ) feature_y
            LEFT JOIN shape_files.parcels_cincy parcels
            ON ST_DWithin(feature_y.geom, parcels.geom, {max_dist}*3.281::double precision)
            AND feature_y.parcel_id <> parcels.parcelid
            GROUP BY feature_y.parcel_id
        ;
        CREATE INDEX ON insp2houses_{max_dist}m (parcel_id);
        """.format(max_dist=max_dist)

    #Create a cursor
    cur = con.cursor()

    #Get the current schema
    cur.execute('SELECT current_schema;')
    current_schema = cur.fetchone()[0]

    #Build the table name
    table_name = 'insp2houses_{max_dist}m'.format(max_dist=max_dist)
    # check if table already exists in current schema;
    # if not, create it
    if table_name not in tables_in_schema(current_schema):
        logging.info("Table %s does not exist yet, generating."%table_name)
        cur.execute(query)
    else:
        logging.info("Table %s already exists, skipping."%table_name)
    
    con.commit()

    ## ------------------------------------------------------------------------
    ## Make the table of nearby events, and the features.
    ## ------------------------------------------------------------------------

    #Get the time window for which you can generate features
    min_insp, max_insp = check_date_boundaries(con, n_months, dataset, date_column)

    query = """
        DROP TABLE IF EXISTS inspfeatures1_{n_months}months_{max_dist}m;
        CREATE TEMP TABLE inspfeatures1_{n_months}months_{max_dist}m ON COMMIT DROP AS
            SELECT t2.parcel_id, t2.inspection_date,
                   t2.event,
                   coalesce(t1.count, 0) as count,
                   (coalesce(t1.count, 0)+1.0) / (coalesce(t2.parcels,0)+5.0) as regularized_count_per_houses 
            FROM (
                SELECT  
                    feature_y.parcel_id,
                    feature_y.inspection_date,
                    coalesce(realinspections.event,'missing') as event,
                    count(*) as count
                FROM (
                    SELECT t.*, p.geom, ih.parcels
                    FROM parcels_inspections t
                    LEFT JOIN shape_files.parcels_cincy p
                    ON t.parcel_id=p.parcelid
                    LEFT JOIN insp2houses_{max_dist}m ih
                    USING (parcel_id)
                ) feature_y
                JOIN (
                    SELECT insp.*, p.geom
                    FROM inspections_views.events_parcel_id insp
                    JOIN shape_files.parcels_cincy p
                    ON insp.parcel_no=p.parcelid
                ) realinspections
                ON realinspections.date < feature_y.inspection_date
                AND (feature_y.inspection_date - '{n_months} month'::interval) <= realinspections.date
                AND ST_DWithin(feature_y.geom, realinspections.geom, {max_dist}*3.281::double precision)
                WHERE feature_y.inspection_date BETWEEN '{min_date}' AND '{max_date}'
                GROUP BY feature_y.parcel_id, feature_y.inspection_date, realinspections.event
            ) t1
            RIGHT JOIN
            (SELECT parcel_id, inspection_date, ft.event, parcels
                FROM parcels_inspections
                JOIN 
                    (select distinct coalesce(event,'missing') as event from inspections_views.events_parcel_id) ft
                ON true
                JOIN insp2houses_{max_dist}m
                USING (parcel_id)
            ) t2
            USING (parcel_id, inspection_date, event)
        ;

        CREATE TEMP TABLE inspfeatures2_{n_months}months_{max_dist}m ON COMMIT DROP AS (
        SELECT parcel_id, inspection_date, event, count
        FROM inspfeatures1_{n_months}months_{max_dist}m
        UNION ALL (
            SELECT parcel_id, inspection_date, 
                   event||'_per_houses' as event,
                   regularized_count_per_houses AS count
            FROM inspfeatures1_{n_months}months_{max_dist}m
            )
        ) ;
        CREATE INDEX ON inspfeatures2_{n_months}months_{max_dist}m (parcel_id, inspection_date);
        
        -- Now call the pivot function to create columns with the 
        -- different inspection events
        SELECT colpivot('insppivot_{n_months}months_{max_dist}m',
                        'select * from inspfeatures2_{n_months}months_{max_dist}m',
                        array['parcel_id','inspection_date'],
                        array['event'],
                        '#.count',
                        null
        ); -- Note: Not coalescing the counts, as the _per_houses shouldn't be
           --       set to 0. We'll have to leave it to later imputation.
        CREATE INDEX ON insppivot_{n_months}months_{max_dist}m (parcel_id, inspection_date);

        -- still need to 'save' the tables into a permanent table
        DROP TABLE IF EXISTS inspfeatures_{n_months}months_{max_dist}m;
        CREATE TABLE inspfeatures_{n_months}months_{max_dist}m AS
            SELECT * FROM insppivot_{n_months}months_{max_dist}m ip1
        ;
        """.format(n_months=str(n_months), max_dist=max_dist, 
                   min_date=str(min_insp), max_date=str(max_insp))

    cur.execute(query)
    con.commit()
    
    # fetch the data
    query = """
        SELECT * FROM inspfeatures_{n_months}months_{max_dist}m;
    """.format(n_months=str(n_months),
               max_dist=max_dist)

    df = pd.read_sql(query, con, index_col=['parcel_id', 'inspection_date'])

    # clean up the column names
    df.columns = map(lambda x: x.replace(' ','_').lower(), df.columns)
    df.columns = map(lambda x: ''.join(c for c in x if c.isalnum() or c=='_'),
                    df.columns)

    # drop the last interim table
    query = 'drop table inspfeatures_{n_months}months_{max_dist}m'.format(
            n_months=str(n_months), max_dist=str(max_dist))
    cur.execute(query)
    con.commit()

    return df

