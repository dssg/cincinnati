
# coding: utf-8

# In[1]:

from sqlalchemy import create_engine
import pandas as pd

from lib_cinci.config import main as config


user = config['db']['user']
password = config['db']['password']
host  = config['db']['host']
database  = config['db']['database']
engine = create_engine('postgresql://{user}:{password}@{host}:5432/{database}'.format(user=user, password=password, host=host, database=database))


# In[3]:

pop_housing_sql = """SELECT census.*, groups.area FROM shape_files.census_pop_housing as census
                    JOIN shape_files.census_blocks_groups as groups
                    on census.tract = groups.tract
                    and census.block_group = groups.blkgrp;"""


# In[4]:

pop_housing_raw = pd.read_sql_query(pop_housing_sql, con=engine)


# # Raw census data

# In[5]:

pop_housing_raw.head()


# # Calculating census features

# list of feature description and calculation can be found in folder docs/data_dictionaries
# 
# features are claculated for each pair of census tract and block 

# In[5]:

features = pd.DataFrame({   'tract' : pop_housing_raw.tract,
                            'block_group' : pop_housing_raw.block_group,
                            'housing_density': pop_housing_raw.H0030001/pop_housing_raw.area,
                            'rate_occupied_units': pop_housing_raw.H0030002/pop_housing_raw.H0030001,
                            'rate_vacant_units': pop_housing_raw.H0030003/pop_housing_raw.H0030001,
                            'rate_mortgage_or_loan' : pop_housing_raw.H0040002/pop_housing_raw.H0030001,
                            'rate_renter_occupied' : pop_housing_raw.H0040004/pop_housing_raw.H0030001,
                            'rate_for_rent' : pop_housing_raw.H0050002/pop_housing_raw.H0030001,
                            'rate_white_householder' : pop_housing_raw.H0060002/pop_housing_raw.P0180001,
                            'rate_black_householder' : pop_housing_raw.H0060003/pop_housing_raw.P0180001,
                            'rate_native_householder' : (pop_housing_raw.H0060004+pop_housing_raw.H0060006)/pop_housing_raw.P0180001,
                            'rate_asian_householder' : pop_housing_raw.H0060005/pop_housing_raw.P0180001,
                            'rate_other_race_householder' : pop_housing_raw.H0060007/pop_housing_raw.P0180001,
                            'rate_pop_occupied_units' : pop_housing_raw.H0100001/pop_housing_raw.P0010001,
                            'rate_1_per_household' : pop_housing_raw.H0130002/pop_housing_raw.P0180001,
                            'rate_2_per_household' : pop_housing_raw.H0130003/pop_housing_raw.P0180001,
                            'rate_3_per_household' : pop_housing_raw.H0130004/pop_housing_raw.P0180001,
                            'rate_4_per_household' : pop_housing_raw.H0130005/pop_housing_raw.P0180001,
                            'rate_5_per_household' : pop_housing_raw.H0130006/pop_housing_raw.P0180001,
                            'rate_6_per_household' : pop_housing_raw.H0130007/pop_housing_raw.P0180001,
                            'rate_7_plus_per_household' : pop_housing_raw.H0130008/pop_housing_raw.P0180001,
                            'rate_owner_occupied' : pop_housing_raw.H0140002/pop_housing_raw.H0030001,
                            'rate_owner_occupied_white' : pop_housing_raw.H0140003/pop_housing_raw.H0140002,
                            'rate_owner_occupied_black' : pop_housing_raw.H0140004/pop_housing_raw.H0140002,
                            'rate_owner_occupied_native' : (pop_housing_raw.H0140005+pop_housing_raw.H0140007)/pop_housing_raw.H0140002,
                            'rate_owner_occupied_asian' : pop_housing_raw.H0140006/pop_housing_raw.H0140002,
                            'rate_owner_occupied_other_race' : pop_housing_raw.H0140008/pop_housing_raw.H0140002,
                            'rate_renter_occupied_white' : pop_housing_raw.H0140011/pop_housing_raw.H0040004,
                            'rate_renter_occupied_black' : pop_housing_raw.H0140012/pop_housing_raw.H0040004,
                            'rate_renter_occupied_native' : (pop_housing_raw.H0140013+pop_housing_raw.H0140015)/pop_housing_raw.H0040004,
                            'rate_renter_occupied_asian' : pop_housing_raw.H0140014/pop_housing_raw.H0040004,
                            'rate_renter_occupied_other' : pop_housing_raw.H0140016/pop_housing_raw.H0040004,
                            'rate_owner_occupied_hispanic' : pop_housing_raw.H0150004/pop_housing_raw.H0140002,
                            #'rate_renter_occupied_hispanic' : pop_housing_raw.H0150005/pop_housing_raw.H0040004,
                            'rate_owner_occupied_w_children' : pop_housing_raw.H0190003/pop_housing_raw.H0140002,
                            'rate_owner_occupied_no_children' : pop_housing_raw.H0190004/pop_housing_raw.H0140002,
                            'rate_renter_occupied_no_children' : 1-(pop_housing_raw.H0190006/pop_housing_raw.H0040004),
                            'rate_renter_occupied_w_children' : pop_housing_raw.H0190006/pop_housing_raw.H0040004,
                            'population_density' : pop_housing_raw.P0010001/pop_housing_raw.area,
                            'rate_white_pop' : pop_housing_raw.P0030002/pop_housing_raw.P0010001,
                            'rate_black_pop' : pop_housing_raw.P0030003/pop_housing_raw.P0010001,
                            'rate_native_pop' : (pop_housing_raw.P0030006+pop_housing_raw.P0030004)/pop_housing_raw.P0010001,
                            'rate_asian_pop' : pop_housing_raw.P0030005/pop_housing_raw.P0010001,
                            'rate_other_race_pop' : pop_housing_raw.P0030007/pop_housing_raw.P0010001,
                            'rate_pop_over_18' : pop_housing_raw.P0110001/pop_housing_raw.P0010001,
                            'rate_male_under_18' : (pop_housing_raw.P0120003+pop_housing_raw.P0120004+pop_housing_raw.P0120005+pop_housing_raw.P0120006)/pop_housing_raw.P0010001,                         
                            'rate_male_18_35' : pop_housing_raw[['P0120007','P0120008','P0120009','P0120010','P0120011','P0120012']].sum(axis=1)/pop_housing_raw.P0010001,                         
                            'rate_male_35_50' : pop_housing_raw[['P0120013','P0120014','P0120015']].sum(axis=1)/pop_housing_raw.P0010001,
                            'rate_male_50_75' : pop_housing_raw[['P0120016',	'P0120017',	'P0120018',	'P0120019',	'P0120020',	'P0120021',	'P0120022']].sum(axis=1)/pop_housing_raw.P0010001,
                            'rate_male_over_75' : pop_housing_raw[['P0120023','P0120024','P0120025']].sum(axis=1)/pop_housing_raw.P0010001,                         
                            'rate_female_under_18' : pop_housing_raw[['P0120027','P0120028','P0120029','P0120030']].sum(axis=1)/pop_housing_raw.P0010001,  
                            'rate_female_18_35' : pop_housing_raw[['P0120031',	'P0120032',	'P0120033',	'P0120034',	'P0120035',	'P0120036']].sum(axis=1)/pop_housing_raw.P0010001,                         
                            'rate_female_35_50' : pop_housing_raw[['P0120037',	'P0120038',	'P0120039']].sum(axis=1)/pop_housing_raw.P0010001,
                            'rate_female_50_75' : pop_housing_raw[['P0120040',	'P0120041',	'P0120042',	'P0120043',	'P0120044',	'P0120045',	'P0120046']].sum(axis=1)/pop_housing_raw.P0010001,
                            'rate_male_over_75' : pop_housing_raw[['P0120047','P0120048','P0120049']].sum(axis=1)/pop_housing_raw.P0010001,
                            'rate_households' : pop_housing_raw.P0180001/pop_housing_raw.H0030001})


# In[7]:

features


# In[10]:

features.to_sql('census_features', engine, schema='shape_files', if_exists='replace', index=False)

