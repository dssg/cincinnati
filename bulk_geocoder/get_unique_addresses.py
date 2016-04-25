import pandas as pd
import os

path_to_etl = os.path.join(os.environ['DATA_FOLDER'], 'etl')
path_to_fire = os.path.join(path_to_etl, 'fire', 'tmp', 'fire_db.csv')
path_to_crime = os.path.join(path_to_etl, 'crime', 'tmp', 'diff_crime_db.csv')
path_to_sales = os.path.join(path_to_etl, 'sales', 'tmp', 'diff_sales_db.csv')
path_to_permits = os.path.join(path_to_etl, 'permits', 'tmp', 'diff_permits_db.csv')

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

print 'Loading permits, fire, crime and sales. If you have more datasets with address add them here...'

print 'Processing permits:'
permits = pd.read_csv(path_to_permits)
permits = process_df(permits)

print 'Processing fire:'
fire = pd.read_csv(path_to_fire)
fire = process_df(fire)

print 'Processing crime'
crime = pd.read_csv(path_to_crime)
crime = process_df(crime)

print 'Processing sales'
sales = pd.read_csv(path_to_sales)
sales = process_df(sales)

print 'Merging'
df = pd.concat([permits, fire, crime, sales])
print '    Merged dataset has {:,d} addresses'.format(len(df.index))
df = df.drop_duplicates(subset='address')
print '    Merged dataset has {:,d} unique addresses'.format(len(df.index))

path_to_save = os.path.join(path_to_etl, 'unique_addresses.csv')
print 'Saving on {}'.format(path_to_save)
df.to_csv(path_to_save, index=False)


