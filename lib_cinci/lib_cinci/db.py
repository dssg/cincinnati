from config import load

#Returns a string contaning a URI for the given database type
#assumes there is a config.yaml file in $ROOT folder with a db
#key contaning host, user, password and database
uri = '{dialect}://{user}:{password}@{host}:5432/{database}'.format(**load('config.yaml')['db'])