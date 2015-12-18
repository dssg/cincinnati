import os
import yaml

#load the config.yaml file
folder = os.environ['ROOT_FOLDER']
name = 'config.yaml'
path = "%s/%s" % (folder, name)
f = open(path, 'r')
text = f.read()
dic = yaml.load(text)
main = dic
