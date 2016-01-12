#!/usr/bin/env python

import logging

from scipy.stats import itemfreq
from sklearn import metrics
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

logger = logging.getLogger(__name__)

def plot_feature_importances(feature_names, feature_importances, filename):
    importances = list(zip(feature_names, list(feature_importances)))
    importances = pd.DataFrame(importances, columns=["Feature", "Importance"])
    importances = importances.set_index("Feature")
    importances = importances.sort(columns="Importance", ascending=False)
    plt.figure()
    plt.style.use('ggplot')
    importances.plot(kind="barh", legend=False)
    plt.tight_layout()
    plt.savefig(filename)


def fifty_fifty_split(labels):
    """
    If there is a dominant class, remove as many occurrences
    of this class until both classes are represented with the same
    number of occurrences.
    :param labels: list of binary 0 and 1
    :return: list of indexes of to keep
    """
    class1_idx = np.where(labels)[0]
    class0_idx = np.where(np.logical_not(labels))[0]

    minority_class_size = min(len(class0_idx), len(class1_idx))
    if minority_class_size == 0:
        raise ValueError("Only one class present, can not make 50/50 split")

    # only keep as many elements as there are in minority class
    # for each class (random selection)
    class0_idx = np.random.choice(class0_idx, minority_class_size,
                                  replace=False)
    class1_idx = np.random.choice(class1_idx, minority_class_size,
                                  replace=False)

    # put majority and minority class indexes back together
    indexes_to_keep = np.concatenate((class0_idx, class1_idx))
    indexes_to_keep = np.sort(indexes_to_keep)

    return indexes_to_keep


def print_model_statistics(y_test_cv, result_cv):
    # Accuracy score
    acc = metrics.accuracy_score(y_test_cv, result_cv)
    acc_str = 'Accuracy score: {:.2%}'.format(acc)
    logger.debug(acc_str)

    # Classification report (precision, recall, F1 score)
    class_rpt = metrics.classification_report(y_test_cv, result_cv)
    logger.debug(class_rpt)

    logger.debug('truth: {}'.format(itemfreq(y_test_cv)))
    logger.debug('model: {}'.format(itemfreq(result_cv)))

    # Classification report for 50-50 split
    logger.debug("Results fifty fifty split")
    indexes_to_keep = fifty_fifty_split(y_test_cv)
    class_rpt = metrics.classification_report(y_test_cv[indexes_to_keep],
                                              result_cv[indexes_to_keep])
    logger.debug(class_rpt)


def print_confusion_matrix(y_test_cv, result_cv):
    cm = metrics.confusion_matrix(y_test_cv, result_cv)
    np.set_printoptions(precision=2)
    logger.debug('Confusion matrix, without normalization')
    logger.debug(cm)


def precision_at_x_percent(test_labels, test_predictions, x_percent=0.01):

    cutoff_index = int(len(test_predictions) * x_percent)
    cutoff_index = min(cutoff_index, len(test_predictions) - 1)

    sorted_by_probability = np.sort(test_predictions)[::-1]
    cutoff_probability = sorted_by_probability[cutoff_index]

    test_predictions_binary = np.copy(test_predictions)
    test_predictions_binary[test_predictions_binary >= cutoff_probability] = 1
    test_predictions_binary[test_predictions_binary < cutoff_probability] = 0

    precision, _, _, _ = metrics.precision_recall_fscore_support(
        test_labels, test_predictions_binary)
    precision = precision[1]  # only interested in precision for label 1

    return cutoff_probability, precision


def plot_precision_at_varying_percent(test_labels, test_predictions):
    percent_range = [0.01 * i for i in range(1, 101)]
    cutoffs_and_precisions = [precision_at_x_percent(test_labels,
                              test_predictions, x_percent=p)
                              for p in percent_range]
    cutoffs, precisions = zip(*cutoffs_and_precisions)
    plt.plot(percent_range, precisions)
    plt.plot(percent_range, cutoffs)

    #Save file in output folder
    path_to_fig = os.path.join(os.environ['OUTPUT_FOLDER'], 'precision_at.png')
    plt.savefig(path_to_fig)
