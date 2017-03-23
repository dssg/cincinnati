import os
import yaml
import pandas as pd 

# load the config.yaml file
folder = os.environ['ROOT_FOLDER']
name = 'config.yaml'
path = "%s/%s" % (folder, name)
f = open(path, 'r')
text = f.read()
main = yaml.load(text)


def load(name):
    folder = os.environ['ROOT_FOLDER']
    path = "%s/%s" % (folder, name)
    with open(path, 'r') as f:
        text = f.read()
    dic = yaml.load(text)
    return dic

def get_config_parameters(experiment_config):
    with open(experiment_config, 'r') as f:
        df = pd.io.json.json_normalize(yaml.load(f))
        df.set_index('experiment_name', drop=False, inplace=True)
        return df

