import logging

# formatter = '%(message)s \t\t\t %(asctime)s %(name)s  %(levelname)s'
formatter = '%(levelname)s %(message)s'
level = logging.DEBUG
logging.basicConfig(level=level, format=formatter)
