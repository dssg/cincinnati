"""
Given a model_id that has performed well historically, train a model with 
this model_id's configuration and parameters, but using all data up to a 
given train_end date. Then, use this model to predict the outcome for all
datapoints in a given prediction_schema. Return the trained model and the
predictions.
"""

from sklearn_evaluation.Logger import Logger
from lib_cinci.config import main as cfg
from lib_cinci import dataset
from lib_cinci.features import parse_feature_pattern_list
from lib_cinci.dataset import get_features_for_inspections_in_schema
import datetime
from sklearn import preprocessing
from pydoc import locate

def get_config(model_id):
    """ Give a model_id (string or ObjectId), return the entire MongoDB log
        for that model.
    """

    logger = Logger(host=cfg['logger']['uri'],
                    db=cfg['logger']['db'],
                    collection=cfg['logger']['collection'])

    return logger.get_doc_from_id(model_id)


def train_on_config(myconfig, n_jobs=-1):

    features = parse_feature_pattern_list(myconfig["config"]["features"])
    start_date = datetime.datetime.strptime(myconfig["config"]["start_date"], '%d%b%Y')
    fake_today = datetime.datetime.strptime(myconfig["config"]['fake_today'], '%d%b%Y')
    only_residential = myconfig["config"]["residential_only"]

    train = dataset.get_training_dataset(
        features=features,
        start_date=start_date,
        end_date=fake_today,
        only_residential=only_residential)

    imputer = preprocessing.Imputer().fit(train.x)
    train.x = imputer.transform(train.x)

    scaler = preprocessing.StandardScaler().fit(train.x)
    train.x = scaler.transform(train.x)

    # Here comes a hack: in the MongoDB, we only store e.g.
    # 'RandomForestClassifier'; but we need '
    # sklearn.ensemble.RandomForestClassifier'. Fortunately, the longer name
    # are stored in myconfig['config']['models']
    modelclasses = [x for x in myconfig['config']['models']
                    if x.endswith(myconfig['name'])]
    if len(modelclasses) > 1:
        raise ValueError('Failed to uniquely identify model %s'%myconfig['name'])

    modelclass = modelclasses[0]
    model = locate(modelclass)(**myconfig['config']['parameters'])

    if hasattr(model, 'n_jobs'):
        model.set_params(n_jobs=n_jobs)

    # SVC does not predict probabilities by default
    if hasattr(model, 'probability'):
        model.probability = True

    model.fit(train.x, train.y)

    return model, imputer, scaler, features

def predict_on_date(prediction_schema,model,imputer,scaler,features):

    dataset = get_features_for_inspections_in_schema(prediction_schema, features)

    # Impute
    dataset.x = imputer.transform(dataset.x)
    # Scale
    dataset.x = scaler.transform(dataset.x)
    # Predict
    preds_proba = model.predict_proba(dataset.x)[:, 1]
    # Convert to Dataset to DataFrame and subselect only the viol_outcome
    # column
    df = dataset.to_df()[['viol_outcome']]
    df['prediction'] = preds_proba

    df = df.reset_index().drop(['inspection_date','viol_outcome'],1)

    return df.set_index('parcel_id')

def main(model_id, train_end_date, prediction_schema, n_jobs=-1):
    """
    Args:
        train_end_date (str): In format like '30Jun2016'
    """

    myconfig = get_config(model_id)

    # drop everything we don't want from the config
    myconfig = {x:myconfig[x] for x in ['name','parameters','config']}
    del myconfig['config']['experiment_name']

    # shift the dates
    start_date = datetime.datetime.strptime(myconfig['config']['start_date'], 
                                            '%d%b%Y')
    fake_today = datetime.datetime.strptime(myconfig['config']['fake_today'], 
                                            '%d%b%Y')
    train_len = fake_today - start_date

    print "Original start date: ", start_date
    print "Original end date: ", fake_today
    print "Train len: ", train_len

    new_fake_today = datetime.datetime.strptime(train_end_date, '%d%b%Y')
    new_start_date = new_fake_today - train_len

    print "new end: ", new_fake_today
    print "new start: ", new_start_date
    print "new len: ", new_fake_today - new_start_date

    # now update the config
    myconfig['config']['start_date'] = datetime.datetime.strftime(new_start_date,
                                                                  '%d%b%Y')
    myconfig['config']['fake_today'] = datetime.datetime.strftime(new_fake_today,
                                                                  '%d%b%Y')

    # train the model
    model, imputer, scaler, features = train_on_config(myconfig, n_jobs)

    # predict on new date
    return predict_on_date(prediction_schema,model,imputer,scaler,features)

if __name__ == '__main__':
    pass
