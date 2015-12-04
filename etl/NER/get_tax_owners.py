"""
Perform name entity recognition for all property owners for all tax years. Store as one csv per year.
"""

import pandas as pd
from sqlalchemy import create_engine

from NER_client import perform_NER

import sys
sys.path.append('../../')
import dbconfig


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
    engine = create_engine('postgresql://{conf.user}:{conf.password}@{conf.host}:5432/{conf.database}'.format(conf=dbconfig))
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
    data.to_csv("owners_{year}_resolved.csv".format(year=year))