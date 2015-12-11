import pandas as pd
import yaml
import sys
from python_ds_tools.config import main as config
from python_ds_tools import data_folder

input_file = sys.argv[1]
year = int(sys.argv[2])

with open('definitions.yaml') as f:
    definitions = yaml.load(f.read())

names = definitions['names'][year]

#Move current directory do all I/O operations take place in the corresponding
#Data folder
data_folder = data_folder.for_file(__file__)
os.chdir(data_folder)

print 'Working in folder: %s' % data_folder

#Create tmp file if it does not exist
if not os.path.exists('tmp'):
    os.makedirs('tmp')

df = pd.read_csv(input_file, names=names)

output = 'tmp/taxes_%d.csv' % year

df.to_csv(output)
