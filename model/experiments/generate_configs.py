import os
import sys
import pandas as pd 
from dateutil import relativedelta

# first argument: folder with YAML templates
# second argument: folder where the sub-folders with configured templates will be written to

def generate_configs(faketodays, training_offsets, validationwindows):

    startdates = {}
    for faketoday in faketodays:
        startdates[faketoday] = [faketoday - offset for offset in training_offsets if (faketoday-offset) >= pd.to_datetime('2013-01-01')]
        # always add the beginning of data as one of the training set startpoints
        startdates[faketoday].append(pd.to_datetime('2013-01-01'))

    # ok, let's generate all the YAMLs
    for faketoday in faketodays:
        for startdate in startdates[faketoday]:

            foldername = os.path.join(OUTPUTFOLDER, startdate.strftime('%d%b%Y') + '_' + faketoday.strftime('%d%b%Y'))
            os.makedirs(foldername)

            for templatefile in os.listdir(TEMPLATEFOLDER):

                for validationwindow in validationwindows:

                    with open(os.path.join(TEMPLATEFOLDER, templatefile),'r') as fin:
                        template = fin.read()
                        experiment = template.format(startdate=startdate.strftime('%d%b%Y'),
                                                     faketoday=faketoday.strftime('%d%b%Y'),
                                                     validationwindow=validationwindow)
                    with open(os.path.join(os.path.abspath(foldername), templatefile), 'wb') as fout:
                        fout.write(experiment)

if __name__=='__main__':

    # quick dirty script to generate a bunch of file experiment configs
    # from the templates, over a range of temporal splits

    # give the script the location of the templates
    TEMPLATEFOLDER = os.path.abspath(sys.argv[1])

    # will put the new folders in this folder
    OUTPUTFOLDER = os.path.abspath(sys.argv[2])

    print "Reading templates from ", TEMPLATEFOLDER
    print "Writing files to new subfolders in", OUTPUTFOLDER

    faketodays = pd.date_range(end='2015-06-30', periods=4, freq='6M')

    training_offsets = [relativedelta.relativedelta(months=x) for x in [12,24]]

    validationwindows=['6Month']

    generate_configs(faketodays, training_offsets, validationwindows)
    generate_configs(pd.date_range(end='2015-12-31', periods=1, freq='8M'),
                     training_offsets, ['8Month'])


