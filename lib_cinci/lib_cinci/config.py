import os
import yaml

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
