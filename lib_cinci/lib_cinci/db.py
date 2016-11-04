from config import load

# Returns a string contaning a URI for the given database type
# assumes there is a config.yaml file in $ROOT folder with a db
# key contaning host, user, password and database
connparams = load('config.yaml')['db']
uri = '{dialect}://{user}:{password}@{host}:{port}/{database}'.format(**connparams)
libpq_uri = 'dbname={database} user={user} host={host} password={password} port={port}'.format(**connparams)
