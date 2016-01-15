"""
Perform name entity recognition for all property owners for all tax years. Store as one csv per year.
"""

import pandas as pd
from sqlalchemy import create_engine
from NER_client import perform_NER
from dstools.config import main as config
from dstools import data_folder
import os

#Move current directory do all I/O operations take place in the corresponding
#Data folder
data_folder = data_folder.for_file(__file__)
os.chdir(data_folder)

print('Changing working dir to: %s' % os.getcwd())

#Create tmp file if it does not exist
if not os.path.exists('tmp'):
    print('Creating tmp folder in %s' % os.getcwd())
    os.makedirs('tmp')


def format_owner(own):
    """
    Capitalize every word and remove part any "&" and every character following that &. This format works well with the
      Stanford library.
    :param own:
    :return:
    """
    if "&" in own:
        own = own.split("&")[0]
    own = " ".join([o.capitalize() for o in own.split()])
    return own


def resolve_entities(data_for_year):
    data_for_year["owner"] = data_for_year["owner"].apply(format_owner)
    data_for_year["entity"] = data_for_year["owner"].apply(perform_NER)
    return data_for_year


def get_data_for_year(year):
    user = config['db']['user']
    password = config['db']['password']
    host  = config['db']['host']
    database  = config['db']['database']
    engine = create_engine('postgresql://{user}:{password}@{host}:5432/{database}'.format(user=user, password=password, host=host, database=database))
    if year == 2015:
        sql = ("SELECT  new_parcel_id AS parcel_id, "
               "CONCAT(CONCAT(owner_name, ' '), owner_attn) AS owner "
               "FROM public.taxes_2015 "
               "WHERE length(new_parcel_id)> 1;")
    else:
        sql = ("SELECT  new_parcel_id AS parcel_id, "
               "CONCAT(CONCAT(OWNER_LINE1, ' '), OWNER_LINE2) AS owner "
               "FROM public.taxes_{year} "
               "WHERE length(new_parcel_id)>1;".format(year=year))

    owners = pd.read_sql(sql, con=engine)
    owners = owners.set_index("parcel_id")
    return owners


for year in range(2007, 2016):
    print (year)
    data = get_data_for_year(year)
    data = resolve_entities(data)
    output = "tmp/owners_{year}_resolved.csv".format(year=year)
    data.to_csv(output)
    print('Result is in %s/%s' % (os.getcwd(), output))
