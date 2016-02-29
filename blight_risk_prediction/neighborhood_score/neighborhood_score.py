#!/usr/bin/env python
import argparse
from string import Template
import os
from lib_cinci.config import main as cfg
from sqlalchemy import create_engine
import psycopg2

def main():
    table_name = 'neighborhood_score_{}m_{}months'.format(args.maxdist,
      args.months)
    print 'Creating {} table...'.format(table_name)
    #Load template
    path_to_template = os.path.join(os.environ['ROOT_FOLDER'],
        'blight_risk_prediction', 'neighborhood_score',
        'neighborhood_score.template.sql')
    with open(path_to_template, 'r') as f:
        sql_script = Template(f.read())
    #Convert max_dist to survey foot, since those are the units in the
    #database
    max_dist_foot = args.maxdist * 3.281
    #Replace with values: schema, table_name, max_dist_foot, n_months
    sql_script = sql_script.substitute(schema=args.schema, table_name=table_name,
        max_dist_foot=max_dist_foot, n_months=args.months)
    #Run on DB
    db = cfg['db']
    con = psycopg2.connect(dbname=db['database'], host=db['host'],
      user=db['user'], password=db['password'])
    cur = con.cursor()
    cur.execute(sql_script)
    con.commit()
    cur.close()
    con.close()
    print 'Done!'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=("Create a table scoring "
        "the sourroundings of each inspection. The objective of this "
        "table is to provide a metric of how blighted is the area nearby "
        "certain parcel within X months of inspection date"))
    parser.add_argument("-m", "--months",
                        help=("Count inspections that happened m months "
                              "before inspection took place. "
                              "Defaults to 3 months"), type=int,
                              default=3)
    parser.add_argument("-md", "--maxdist",
                        help=("Count inspections that happened max m meters "
                              "from inspection. "
                              "Defaults to 1000 m (max value posible)"), type=int,
                        default=1000)
    parser.add_argument("-s", "--schema",
                        help=("Databse schema to use, this determines where the "
                              "table is created and where to look for the "
                              "inspections_parcels table. Defautls to 'features'"),
                        type=str, default='features')
    args = parser.parse_args()    
    main()