import numpy as np
from sklearn.metrics import precision_score


def precision_at(labels, scores, percent=0.01, ignore_nas=False):
    '''
    Calculates precision at a given percent.
    Only supports binary classification.
    '''
    #Sort scores in descending order    
    scores_sorted = np.sort(scores)[::-1]

    #Based on the percent, get the index to split the data
    #if value is negative, return 0
    cutoff_index = max(int(len(labels) * percent) - 1, 0)
    #Get the cutoff value
    cutoff_value = scores_sorted[cutoff_index]

    #Convert scores to binary, by comparing them with the cutoff value
    scores_binary = np.array(map(lambda x: int(x>=cutoff_value), scores))
    #Calculate precision using sklearn function
    if ignore_nas:
        precision = __precision(labels, scores_binary)
    else:
        precision = precision_score(labels, scores_binary)

    return precision, cutoff_value


def __threshold_at_percent(y_true, y_score, percent):
    #Sort scores in descending order    
    scores_sorted = np.sort(y_score)[::-1]
    #Based on the percent, get the index to split the data
    #if value is negative, return 0
    threshold_index = max(int(len(y_true) * percent) - 1, 0)
    #Get the cutoff value
    threshold_value = scores_sorted[threshold_index]
    return threshold_value

def __binarize_scores_at_percent(y_true, y_score, percent):
    threshold_value = __threshold_at_percent(y_true, y_score, percent)
    y_score_binary = np.array(map(lambda x: int(x>=threshold_value), y_score))
    return y_score_binary

def __precision(y_true, y_pred):
    '''
        Precision metric tolerant to unlabeled data in y_true,
        NA values are ignored for the precision calculation
    '''
    #precision = tp/(tp+fp)
    #True nehatives do not affect precision value, so for every missing
    #value in y_true, replace it with 0 and also replace the value
    #in y_pred with 0
    is_nan = np.isnan(y_true)
    y_true[is_nan] = 0
    y_pred[is_nan] = 0
    precision = precision_score(y_true, y_pred)
    return precision

def tp_and_fp_at_percent(y_true, y_score, percent):
    y_pred = __binarize_scores_at_percent(y_true, y_score, percent)
    tp = (y_pred == 1) & (y_true == 1)
    fp = (y_pred == 1) & (y_true == 0)
    return tp.sum(), fp.sum()

def tn_and_fn_at_percent(y_true, y_score, percent):
    y_pred = __binarize_scores_at_percent(y_true, y_score, percent)
    tn = (y_pred == 0) & (y_true == 0)
    fn = (y_pred == 0) & (y_true == 1)
    return tn.sum(), fn.sum()


