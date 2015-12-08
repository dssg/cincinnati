from datetime import datetime
import sys

"""
Do some basic data cleaning and conversion on our crime data
"""

order = ['incident_number', 'date_reported', "offense_title", "location", "address", "weekday",
         "rpt_area", "neighbourhood", "hour_from", "hour_to", "weapon", "ucr"]


print (";".join(order))

file_path = sys.argv[1]

with open(file_path) as f:
    i = 0
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
        converted["date_reported"] = datetime(year=int(raw[4]), month=int(raw[2]), day=int(raw[3]),
                                              hour=int(raw[5]), minute=int(raw[6]))
        converted["offense_title"] = raw[7]
        converted["location"] = raw[8]
        converted["address"] = raw[9]
        converted["weekday"] = raw[10]
        converted["rpt_area"] = raw[11]
        converted["neighbourhood"] = raw[12]
        converted["hour_from"] = int(raw[13]) if len(raw[13]) > 0 else ''
        converted["hour_to"] = int(raw[14]) if len(raw[14]) > 0 else ''
        converted["weapon"] = raw[15]
        converted["ucr"] = int(raw[16])

        # print ordered column data
        ordered = [str(converted[col]) for col in order]
        print (";".join(ordered))

