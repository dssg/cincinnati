#!/usr/bin/env python
import argparse

def main():
    print 'Creating {}{} table'.format(args.months, args.maxdist)
    #Convert meters to US survey foot
    #Load template
    #Replace with values: schema, tablename, max_dist_foot, n_months
    #Run on DB

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=("Create a table scoring "
        "the sourroundings of each inspection. The objective of this "
        "table is to provide a metric of how blighted is the area nearby "
        "certain parcel within X months of inspection date"))
    parser.add_argument("-m", "--months",
                        help=("Count inspections that happened m months "
                              "before inspection took place. "
                              "Defaults to 3 months"), type=int,
                              default=3)
    parser.add_argument("-md", "--maxdist",
                        help=("Count inspections that happened max m meters "
                              "from inspection. "
                              "Defaults to 1000 m (max value posible)"), type=int,
                        default=1000)
    args = parser.parse_args()    
    main()