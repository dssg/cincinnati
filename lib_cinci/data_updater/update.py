#!/usr/bin/env python
import logging
import logging.config
import argparse
import urllib2
import os

import dataset #this is really slow since it gets the entire db schema when connection
import pandas as pd
import yaml

from lib_cinci.db import uri
from lib_cinci.config import load
from lib_cinci import data_folder

if __name__ == '__main__':
    #Configure logger
    logging.config.dictConfig(load('logger_config.yaml'))
    logger = logging.getLogger()

    #Step zero: read from yaml file
    parser = argparse.ArgumentParser()
    parser.add_argument("update_file", help="Path to yaml file with configuration parameters")
    args = parser.parse_args()

    with open(args.update_file, 'r') as f:
        params = yaml.load(f)

    db_column = params['storage']['column']
    file_column = params['source']['column']
    #schema = 'public'

    #Folder to use for I/O
    folder = data_folder.for_file(args.update_file)
    os.chdir(folder)
    logger.info('Using {} for I/O operations'.format(folder))

    #Step one: download file from remote server if user provided url
    try:
        url = params['source']['url']
    except Exception, e:
        logger.info('URL was not present in the configuration file...')
    else:
        logger.info('Downloading file...'.format(folder))
        data_file = urllib2.urlopen(url)
        #Dowload file replacing it if already exists
        with open(params['source']['filename'],'wb') as output:
            output.write(data_file.read())

    #Step two: check most recent entry in the database
    db = dataset.connect(uri)
    table_name = params['storage']['table']
    table = db[table_name]
    
    #Query the database, if returns None, the table doesn't exist
    most_recent_row = table.find_one(order_by='-'+db_column)
    if most_recent_row is None:
        db_most_recent = None
        logger.info('Table does not exist, diff file will be a copy of source file')
    else:
        db_most_recent = most_recent_row[db_column]
        logger.info('Most recent record in database is: {}'.format(db_most_recent))
    
    #Step three: load and subset the file to include new entries
    #TO DO: avoid loading if most_recent_row is None
    logger.info('Loading {}'.format(params['source']['filename']))
    df = pd.read_csv(params['source']['filename'])
    df[file_column] = pd.to_datetime(df[file_column])

    #Subset only if db_most_recent has a value    
    new_entries = df[df[file_column] > db_most_recent] if db_most_recent else df
    logger.info('{:,d} new enties'.format(new_entries.shape[0]))
    
    #Step four: save new entries in a csv file
    diff_file = 'tmp/diff_{}.csv'.format(table_name)
    new_entries.to_csv(diff_file, index=False)
    logger.info('New entries saved in {}'.format(os.path.join(folder, diff_file)))