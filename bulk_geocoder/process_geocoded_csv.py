#The responsibility of geocode_csv.py is to simply
#add new columns with the census api data
#this script removes some old columns before uploading data
#to the db
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input", help=("Input csv file to geocode. Format "
                                   "should be the one that is the output "
                                   "of geocode_csv script"),
                    type=str)
parser.add_argument("output", help="Geocoded file ready to to go to the db", type=str)
parser.add_argument("-sep", "--separator", help="separator in the file, defaults to ','",
                    type=str, default=',')
args = parser.parse_args()

print 'Processing csv file...'
print 'Dropping some columns and remaning others...'

df = pd.read_csv(args.input, sep=args.separator)

#We don't really need state and city information
to_drop = ['state', 'city', 'city_census', 'state_census']
df.drop(to_drop, axis=1, inplace=True)

#Also delete the long formatted string with the complete address
#And delete the raw_zip column
df.drop(['geocoded_address', 'zip'], axis=1, inplace=True)

#Rename some columns
df.rename(columns={'zip_census':'zip',
                   'address': 'address_raw',
                   'address_census':'address'},
                   inplace=True)

df.to_csv(args.output)
