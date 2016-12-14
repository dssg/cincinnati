big = {
    "sklearn.ensemble.RandomForestClassifier": {
        'n_estimators': [10,100,1000,5000],
	'criterion' : ['gini', 'entropy'],
        'max_depth': [1,5,10,20,50,100],
        'max_features': ['sqrt','log2'],
        'min_samples_split': [2,5,10]
    },

    "sklearn.linear_model.LogisticRegression": {
        'penalty': ['l1','l2'],
        'C': [0.00001,0.0001,0.001,0.01,0.1,1,10]
    },
    
    "sklearn.ensemble.ExtraTreesClassifier": {
        'n_estimators': [1,10,100,1000,5000],
        'criterion' : ['gini', 'entropy'],
        'max_depth': [1,5,10,20,50,100],
        'max_features': ['sqrt','log2'],
        'min_samples_split': [2,5,10]
    }
}

medium = {
    "sklearn.ensemble.RandomForestClassifier": {
        'n_estimators': [10,100,1000,5000],
	    'criterion' : ['gini', 'entropy'],
        'max_depth': [10,50,100],
        'max_features': ['sqrt','log2'],
        'min_samples_split': [2,5,10]
    },

    "sklearn.ensemble.ExtraTreesClassifier": {
        'n_estimators': [10,100,1000,5000],
        'criterion' : ['gini', 'entropy'],
        'max_depth': [10,50,100],
        'max_features': ['sqrt','log2'],
        'min_samples_split': [2,5,10]
    }
}

small = {
    "sklearn.ensemble.RandomForestClassifier": {
        'n_estimators': [1000,5000]
    }
}

single = {
    "sklearn.ensemble.RandomForestClassifier": {
        'n_estimators': [1000],
        'max_depth': [100],
        'max_features': ['sqrt'],
        'criterion': ['entropy']
    }
}
