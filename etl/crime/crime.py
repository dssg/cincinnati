import dateutil
import sys

"""
Do some basic data cleaning and conversion on our crime data
"""

order = ['incident_number', 'date_reported', "offense_title", "location", "address", "weekday",
         "rpt_area", "neighbourhood", "hour_from", "hour_to", "weapon", "ucr"]


print (";".join(order))

file_path = sys.argv[1]

with open(file_path) as f:
    for r in f.readlines():
        # don't care about the header lines
        if r.startswith("INCIDENT_NO	"):
            continue

        # make sure we can use ";" as delimiter
        assert(";" not in r)

        # too much weird windows whitespace going on
        raw = r.split("\t")
        raw = [c.strip() for c in raw]

        # some data conversions, will make sure that everything that should be int actually is
        converted = dict()
        converted["incident_number"] = raw[0]
        converted["date_reported"] = dateutil.parser.parse(raw[1])
        converted["offense_title"] = raw[2]
        converted["location"] = raw[3]
        converted["address"] = raw[4]
        converted["weekday"] = raw[5]
        converted["rpt_area"] = raw[6]
        converted["neighbourhood"] = raw[7]
        converted["hour_from"] = int(raw[8]) if len(raw[8]) > 0 else ''
        converted["hour_to"] = int(raw[9]) if len(raw[9]) > 0 else ''
        converted["weapon"] = raw[10]
        converted["ucr"] = int(raw[11])

        # print ordered column data
        ordered = [str(converted[col]) for col in order]
        print (";".join(ordered))

