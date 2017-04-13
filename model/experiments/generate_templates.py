import os
import sys
import pandas as pd 
from dateutil import relativedelta
import yaml
import argparse
from itertools import product

# command line argument: the output folder to which the templates will be written

SPACETIMEFEATURES = ['fire','crime','sales','permits','three11']
INSPECTIONFEATURES = ['density']
PARCELFEATURES = ['tax.%','census_2010.rate_%','named_entities.%','parc_area.%',
        'parc_year.%','house_type.%','quarter.%','sixweeksweather.%']

# these fields will be filled by generate_configs.py
CFG = {'start_date': '{startdate}',
       'fake_today': '{faketoday}',
        'validation_window': '{validationwindow}',
        'residential_only': False}

if __name__=='__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--out",
                        help=("Folder to store the generated templates."), type=str)

    parser.add_argument('-md','--maxdist', nargs='+', help='List of '
            'meters that the spacetime features should be aggregated to.', 
            required=True, type=int)
    
    parser.add_argument('-m','--months', nargs='+', help='List of '
            'months that the spacetime features should be aggregated to.', 
            required=True, type=int)

    parser.add_argument('-ms','--modelsize', help=("Size of model grid."),
                        choices=['single','small','medium','big'], type=str)

    parser.add_argument('-a','--algorithms', nargs='+', help='List of '
            'sklearn algorithms to run.', 
            required=True)

    args = parser.parse_args()

    templatefolder = os.path.abspath(args.out)

    modelnames = [x.split('.')[2][:4] for x in args.algorithms]
    modelnames = ''.join(modelnames)
    mytemplate = '{feat}_{md}m_{m}months.%'

    for md_idx in range(len(args.maxdist)):
        for m_idx in range(len(args.months)):

            thiscfg = CFG.copy()
            thiscfg['grid_size'] = args.modelsize
            thiscfg['models'] = args.algorithms

            md = args.maxdist[md_idx]
            m = args.months[m_idx]

            spacetime_only = [mytemplate.format(feat=f, md=md, m=m) for f in SPACETIMEFEATURES]
            inspection_only = [mytemplate.format(feat=f, md=md, m=m) for f in INSPECTIONFEATURES]

            spacetime_upto = [mytemplate.format(feat=f, md=md, m=m) for f,md,m in 
                    product(SPACETIMEFEATURES,args.maxdist[:md_idx+1],args.months[:m_idx+1])
                        ]
            inspection_upto = [mytemplate.format(feat=f, md=md, m=m) for f,md,m in 
                    product(INSPECTIONFEATURES,args.maxdist[:md_idx+1],args.months[:m_idx+1])
                        ]

            # make a config with just parcel features
            thiscfg['features'] = PARCELFEATURES 
            name = 'parcel_only_grid_%s_algos_%s'%(args.modelsize,modelnames)
            thiscfg['experiment_name'] = 'fall2016_{startdate}_{faketoday}_{validationwindow}_' + name
            with open(os.path.join(templatefolder, '%s.yaml'%name),'w') as fout:
                    yaml.dump(thiscfg, fout, default_flow_style=False)

            # make a config with parcel features and only this time and space aggregation
            thiscfg['features'] = PARCELFEATURES + spacetime_only
            name =  'only_%dm_%dmonths_no_density_grid_%s_algos_%s'%(md,m,args.modelsize,modelnames)
            thiscfg['experiment_name'] = 'fall2016_{startdate}_{faketoday}_{validationwindow}_' + name
            with open(os.path.join(templatefolder, '%s.yaml'%name),'w') as fout:
                    yaml.dump(thiscfg, fout, default_flow_style=False)

            # make a config with parcel features and only this time and space density
            thiscfg['features'] = PARCELFEATURES + inspection_only
            name = 'only_%dm_%dmonths_only_density_grid_%s_algos_%s'%(md,m,args.modelsize,modelnames)
            thiscfg['experiment_name'] = 'fall2016_{startdate}_{faketoday}_{validationwindow}_' + name
            with open(os.path.join(templatefolder, '%s.yaml'%name),'w') as fout:
                    yaml.dump(thiscfg, fout, default_flow_style=False)
    
            # make a config with parcel features and up to this space and time
            thiscfg['features'] = PARCELFEATURES + spacetime_upto
            name = 'upto_%dm_%dmonths_no_density_grid_%s_algos_%s'%(md,m,args.modelsize,modelnames)
            thiscfg['experiment_name'] = 'fall2016_{startdate}_{faketoday}_{validationwindow}_' + name
            with open(os.path.join(templatefolder, '%s.yaml'%name),'w') as fout:
                    yaml.dump(thiscfg, fout, default_flow_style=False)

            # make a config with parcel features and up to this space and time, including density
            thiscfg['features'] = PARCELFEATURES + spacetime_upto + inspection_upto
            name = 'upto_%dm_%dmonths_with_density_grid_%s_algos_%s'%(md,m,args.modelsize,modelnames)
            thiscfg['experiment_name'] = 'fall2016_{startdate}_{faketoday}_{validationwindow}_' + name
            with open(os.path.join(templatefolder, '%s.yaml'%name),'w') as fout:
                    yaml.dump(thiscfg, fout, default_flow_style=False)

            # make a config with parcel features and up to this space and time, only density
            thiscfg['features'] = PARCELFEATURES + inspection_upto
            name = 'upto_%dm_%dmonths_only_density_grid_%s_algos_%s'%(md,m,args.modelsize,modelnames)
            thiscfg['experiment_name'] = 'fall2016_{startdate}_{faketoday}_{validationwindow}_' + name
            with open(os.path.join(templatefolder, '%s.yaml'%name),'w') as fout:
                    yaml.dump(thiscfg, fout, default_flow_style=False)



