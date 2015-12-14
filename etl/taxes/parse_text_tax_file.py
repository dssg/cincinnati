import os
import pandas as pd
import numpy as np
import yaml
import sys
from python_ds_tools.config import main as config
from python_ds_tools import data_folder

input_file = sys.argv[1]
year = int(sys.argv[2])

print 'Loading definitions.yaml from: %s' % os.getcwd()

with open('definitions.yaml') as f:
    definitions = yaml.load(f.read())

names = definitions['names'][year]
widths = definitions['sizes'][year]

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

df = pd.read_fwf(input_file, names=names, widths=widths)

output = 'tmp/taxes_%d.csv' % year

df.to_csv(output, index=False)

print 'Result is in %s/%s' % (os.getcwd(), output)
