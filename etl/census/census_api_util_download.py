
# coding: utf-8

# In[2]:

import census_api_util as api
from sqlalchemy import create_engine
import pandas as pd
#test query_census_api function
from lib_cinci.config import main as config




# In[3]:

user = config['db']['user']
password = config['db']['password']
host  = config['db']['host']
database  = config['db']['database']
engine = create_engine('postgresql://{user}:{password}@{host}:5432/{database}'.format(user=user, password=password, host=host, database=database))


# Look up columns for all tracts/block groups from 2010 decimal census
# (bunched in groups of 20 due to api quatas)

# In[4]:

census_20 = api.query_census_api('census',39, '061','*','*',['H0030001',	'H0030002',	'H0030003',	'H0040002',	'H0040004',	'H0050002',	'H0060002',	'H0060003',	'H0060004',	'H0060005',	'H0060006',	'H0060007',	'H0060008',	'H0100001',	'H0130002',	'H0130003',	'H0130004',	'H0130005',	'H0130006',	'H0130007'], 2010, 'a6e317918af5d4097d792cabd992f41f2691b75e', verbose=True)
census_40 = api.query_census_api('census',39, '061','*','*',['H0130008',	'H0140002',	'H0140003',	'H0140004',	'H0140005',	'H0140006',	'H0140007',	'H0140008',	'H0140009',	'H0140010',	'H0140011',	'H0140012',	'H0140013',	'H0140014',	'H0140015',	'H0140016',	'H0140017',	'H0150001',	'H0150002',	'H0150003'], 2010, 'a6e317918af5d4097d792cabd992f41f2691b75e', verbose=True)
census_60 = api.query_census_api('census',39, '061','*','*',['H0150004',	'H0150005',	'H0150006',	'H0150007',	'H0190003',	'H0190004',	'H0190005',	'H0190006',	'H0190007',	'H0200002',	'H0200003',	'P0010001',	'P0030002',	'P0030003',	'P0030004',	'P0030005',	'P0030006',	'P0030007',	'P0030008',	'P0110001'], 2010, 'a6e317918af5d4097d792cabd992f41f2691b75e', verbose=True)
census_80 = api.query_census_api('census',39, '061','*','*',['P0120003',	'P0120004',	'P0120005',	'P0120006',	'P0120007',	'P0120008',	'P0120009',	'P0120010',	'P0120011',	'P0120012',	'P0120013',	'P0120014',	'P0120015',	'P0120016',	'P0120017',	'P0120018',	'P0120019',	'P0120020',	'P0120021',	'P0120022'], 2010, 'a6e317918af5d4097d792cabd992f41f2691b75e', verbose=True)
census_100 = api.query_census_api('census',39, '061','*','*',['P0120023',	'P0120024',	'P0120025',	'P0120026',	'P0120027',	'P0120028',	'P0120029',	'P0120030',	'P0120031',	'P0120032',	'P0120033',	'P0120034',	'P0120035',	'P0120036',	'P0120037',	'P0120038',	'P0120039',	'P0120040',	'P0120041',	'P0120042'], 2010, 'a6e317918af5d4097d792cabd992f41f2691b75e', verbose=True)
census_111 = api.query_census_api('census',39, '061','*','*',['P0120043',	'P0120044',	'P0120045',	'P0120046',	'P0120047',	'P0120048',	'P0120049',	'P0180001',	'P0180002',	'P0180003',	'P0180004'], 2010, 'a6e317918af5d4097d792cabd992f41f2691b75e', verbose=True)


# In[5]:

#look up same values from 2000 census
census_00_20 = api.query_census_api('census',39, '061','*','*',['H003001'], 2000, 'a6e317918af5d4097d792cabd992f41f2691b75e', verbose=True)


# merge all dataframes to one based on pairs of tracts and block groups and drop 'state' and 'county' columns

# In[5]:

census_df = [census_20, census_40, census_60, census_80, census_100, census_111]


# In[6]:

census_df_clean = [df.drop(['state', 'county'], axis=1) for df in census_df]


# In[7]:

census_df_clean[0].head()


# In[8]:

census_pop_housing = reduce(lambda left,right: pd.merge(left,right,on=['tract','block group']), census_df_clean)


# In[21]:

census_pop_housing.rename(columns={'block group': 'block_group'}, inplace=True)


# In[24]:

census_pop_housing.to_sql('census_pop_housing', engine, schema='shape_files', if_exists='replace')

