import os
import pandas as pd
import yaml
import sys
from dstools.config import main as config
from dstools import data_folder
import numpy as np

input_file = sys.argv[1]
year = int(sys.argv[2])

#Set folder where this file is located as working direcory
script_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(script_dir)

print 'Loading definitions.yaml from: %s' % os.getcwd()

with open('definitions.yaml') as f:
    definitions = yaml.load(f.read())

names = definitions['names'][year]

#Move current directory do all I/O operations take place in the corresponding
#Data folder
data_folder = data_folder.for_file(__file__)
os.chdir(data_folder)

print 'Changing working dir to: %s' % os.getcwd()

#Create tmp file if it does not exist
if not os.path.exists('tmp'):
    print 'Creating tmp folder in %s' % os.getcwd()
    os.makedirs('tmp')

print 'Loading data from %d...' % year

#Force all columns to be read as strings to prevent pandas elminating leading 0s
#and other weird stuff. The are some columns with only one blank space, interpret those
#as NA
df = pd.read_csv(input_file, names=names, dtype=np.str, na_values=[' '])

#Create property number
df['property_number'] = df['book'] + df['page'] + df['parcel'] + df['mltown']

output = 'tmp/taxes_%d.csv' % year

df.to_csv(output, index=False)

print 'Result is in %s/%s' % (os.getcwd(), output)
