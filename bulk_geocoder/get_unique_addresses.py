import pandas as pd
import os

path_to_etl = os.path.join(os.environ['DATA_FOLDER'], 'etl')
path_to_fire = os.path.join(path_to_etl, 'fire', 'tmp', 'fire_db.csv')
path_to_crime = os.path.join(path_to_etl, 'crime', 'tmp', 'crime_db.csv')
#path_to_sales = os.path.join(path_to_etl, 'sales', 'tmp', 'sales_db.csv')

def process_df(df):
    print '    Dataset has {:,d} rows and {:,d} columns'.format(*df.shape)
    #Subset to location only columns
    df = df[['address', 'zip', 'latitude', 'longitude']]
    #Drop elements without location data
    df = df[df.address.notnull()]
    print '    Dataset has {:,d} rows with addresses'.format(len(df.index))
    df = df.drop_duplicates(subset='address')
    print '    Dataset has {:,d} unique addresses'.format(len(df.index))
    return df

print 'Loading fire and crime. If you have more datasets with address add them here...'

print 'Processing fire:'
fire = pd.read_csv(path_to_fire)
fire = process_df(fire)

print 'Processing crime'
crime = pd.read_csv(path_to_crime)
crime = process_df(crime)

print 'Merging'
df = pd.concat([fire, crime])
print '    Merged dataset has {:,d} addresses'.format(len(df.index))
df = df.drop_duplicates(subset='address')
print '    Merged dataset has {:,d} unique addresses'.format(len(df.index))



