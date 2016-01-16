big = {
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

medium = {
    "sklearn.ensemble.RandomForestClassifier": {
        'n_estimators': [1,10,100],
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
        'C': [0.01,0.1,1,10],
        'kernel': ['linear']
    }
}