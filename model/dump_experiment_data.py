from lib_cinci import dataset
import os
import yaml
import pandas as pd
from features import feature_parser
import argparse
from lib_cinci.config import main as cfg_main
from lib_cinci.config import load
from model import make_datasets, configure_model
from metta import metta_io
import re


def main(configs, outfolder):

    for config in configs:

        cfg, _ = configure_model(config)
        train, test  = make_datasets(cfg, predictset=False)

        start_date = datetime.datetime.strptime(cfg["start_date"], '%d%b%Y')
        fake_today = datetime.datetime.strptime(cfg['fake_today'], '%d%b%Y')

        # parse the validation window
        dnum, units = re.match(r"(\d+)(\w+)", cfg["validation_window"]).groups() 
        if float(dnum)%1 != 0:
            raise ValueError("The validation window needs an integer!")
        dnum = int(dnum)
        units = units.lower()
        unitdict = {'month':'M', 'day':'D'}
        if units not in unitdict.keys():
            raise ValueError("Validation window units need to be 'Month' or 'Day'!")
        training_end = pd.date_range(start=fake_today, periods=2, 
                                     freq='%d%s'%(dnum,unitdict[units]))[1]
        training_end = training_end.to_datetime()

        train_config = {
                'start_time': start_date # very first data entering frame
                'end_time':  training_end,
                'prediction_window': 1 # just 1 day for us, as features go up to inspection
                'labelname': 'viol_outcome',
                'labeltype': 'binary',
                'feature_names':
                }

        metta_io.archive_train_test(train_config, 
                                    df_train=train.to_df(),
                                    title_train=cfg['experiment_name']+'_train',
                                    test_config, 
                                    df_test=test.to_df(),
                                    title_test=cfg['experiment_name']+'_test',
                                    directory=outfolder,
                                    format='hd5')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--paths_to_config_files', nargs='+', 
        help=('List of paths to config files; all train/test data from '
            'these configs will be dumped.',
            required=True, type=str)
    parser.add_argument("-o", "--outfolder",
                        help="Folder in which the dumped dataframes will be stored.",
                        type=str)
    args = parser.parse_args()

    configs = []
    for f in args.paths_to_config_files:
        with open(args.path_to_config_file, 'r') as f:
            configs.append(yaml.load(f))

    main(configs=configs, outfolder=args.outfolder)
