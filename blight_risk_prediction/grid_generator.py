#This python script generates several models given its name on
#sklearn
import itertools
from pydoc import locate
from grid_values import small_grid

_grid_values = small_grid

def _generate_grid(model_parameters):
    #Iterate over keys and values
    parameter_groups = []
    for key in model_parameters:
        #Generate tuple key,value
        t = list(itertools.product([key], model_parameters[key]))
        parameter_groups.append(t)
    #Cross product over each group
    parameters = list(itertools.product(*parameter_groups))
    #Convert each result to dict
    dicts = [_tuples2dict(params) for params in parameters]
    return dicts

def _tuples2dict(tuples):
    return dict((x, y) for x, y in tuples)


def grid_from_class(class_name):
    #Get grid values for the given class
    values = _grid_values[class_name]
    #Generate cross product for all given values and return them as dicts
    grids = _generate_grid(values)
    #instantiate a model for each grid
    models = [locate(class_name)(**g) for g in grids]
    return models
