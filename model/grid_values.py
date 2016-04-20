big = {
    "sklearn.ensemble.RandomForestClassifier": {
        'n_estimators': [1,10,100,1000],
	'criterion' : ['gini', 'entropy'],
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
    },

    "sklearn.ensemble.ExtraTreesClassifier": {
        'n_estimators': [1,10,100,1000,10000],
        'criterion' : ['gini', 'entropy'],
        'max_depth': [1,5,10,20,50,100],
        'max_features': ['sqrt','log2'],
        'min_samples_split': [2,5,10]
    },

    "sklearn.ensemble.GradientBoostingClassifier": {
        'n_estimators': [1,10,100,1000,10000],
        'learning_rate' : [0.001,0.01,0.05,0.1,0.5],
        'subsample' : [0.1,0.5,1.0],
        'max_depth': [1,3,5,10,20,50,100]
    }
}

medium = {
    "sklearn.ensemble.RandomForestClassifier": {
        'n_estimators': [1,10,100],
	    'criterion' : ['gini', 'entropy'],
        'max_depth': [10,50,100],
        'max_features': ['sqrt','log2'],
        'min_samples_split': [2,5,10]
    },

    "sklearn.ensemble.AdaBoostClassifier": {
        'algorithm': ['SAMME', 'SAMME.R'],
        'n_estimators': [10,100,1000]
    },
    
    "sklearn.linear_model.LogisticRegression": {
        'penalty': ['l1','l2'],
        'C': [0.001,0.01,0.1,1,10]
    },
    
    "sklearn.svm.SVC": {
        'C': [0.001,0.01,0.1,1,10],
        'kernel': ['linear']
    },

    "sklearn.ensemble.ExtraTreesClassifier": {
        'n_estimators': [1,10,100],
        'criterion' : ['gini', 'entropy'],
        'max_depth': [10,50,100],
        'max_features': ['sqrt','log2'],
        'min_samples_split': [2,5,10]
    },

    "sklearn.ensemble.GradientBoostingClassifier": {
        'n_estimators': [1,10,100],
        'learning_rate' : [0.01,0.05,0.1],
        'subsample' : [0.1,0.5,1.0],
        'max_depth': [5,10,50]
    }
}

small = {
    "sklearn.ensemble.RandomForestClassifier": {
        'n_estimators': [10, 100],
        'max_features': ['sqrt','log2'],
    },

    "sklearn.ensemble.AdaBoostClassifier": {
        'algorithm': ['SAMME', 'SAMME.R'],
        'n_estimators': [10,100]
    },
    
    "sklearn.linear_model.LogisticRegression": {
        'penalty': ['l1','l2'],
        'C': [0.01,0.1,1]
    },
    
    "sklearn.svm.SVC": {
        'C': [0.01,0.1,1],
        'kernel': ['linear']
    },

    "sklearn.ensemble.ExtraTreesClassifier": {
        'n_estimators': [10,100],
        'max_features': ['sqrt','log2'],
    },

    "sklearn.ensemble.GradientBoostingClassifier": {
        'n_estimators': [10,100],
        'learning_rate' : [0.05,0.1],
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
