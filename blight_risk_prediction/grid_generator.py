#This python script generates several models given its name on
#sklearn
import itertools
from pydoc import locate

_grid_values = {
    "sklearn.ensemble.RandomForestClassifier": {
        'n_estimators': [1,10,100,1000,10000],
        'max_depth': [1,5,10,20,50,100],
        'max_features': ['sqrt','log2'],
        'min_samples_split': [2,5,10]
    },

    "sklearn.ensemble.AdaBoostClassifier": {
        'algorithm': ['SAMME', 'SAMME.R'],
        'n_estimators': [1,10,100,1000,10000]
    },
    
    "sklearn.linear_model.LogisticRegression": {
        'penalty': ['l1','l2'],
        'C': [0.00001,0.0001,0.001,0.01,0.1,1,10]
    },
    
    "sklearn.svm.SVC": {
        'C': [0.00001,0.0001,0.001,0.01,0.1,1,10],
        'kernel': ['linear']
    }
}

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
