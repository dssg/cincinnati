"""
Extract data from txt file and output tab-delimited csv data.
"""

from attributes import attributes
from util import configure_split
import sys

input_file = sys.argv[1]

print 'Working in folder: %s' % data_folder

columns, types, sizes, descriptions = zip(*attributes)
split_line = configure_split(sizes)

print("\t".join(columns))
with open(input_file) as f:
    for line_raw in f.readlines():
        line_split = split_line(line_raw)
        print("\t".join(line_split))
