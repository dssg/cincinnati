import numpy as np
from numpy.testing import assert_array_equal
from nose.tools import raises
import unittest

from blight_risk_prediction import evaluation


class TestFiftyFiftySplit(unittest.TestCase):
    # equal number of labels for 0 and 1 classes -> keep everything
    def test_same_size(self):

        labels = np.array([1, 0, 0, 1, 0, 1, 1, 0])
        expected = np.array([0, 1, 2, 3, 4, 5, 6, 7])

        actual = evaluation.fifty_fifty_split(np.array(labels))
        assert_array_equal(expected, actual)


    # fewer number of labels for 0 than for 1 class -> throw out some 1
    def test_fewer_0(self):

        np.random.seed(1234)  # "expected" below only valid for this seed

        labels = np.array([1, 0, 1, 1, 1, 1, 1, 0])
        expected = np.array([1, 2, 3, 7])

        actual = evaluation.fifty_fifty_split(np.array(labels))
        assert_array_equal(expected, actual)

    # fewer number of labels for 1 than for 0 class -> throw out some 0
    def test_fewer_1(self):

        np.random.seed(1234)  # "expected" below only valid for this seed

        labels = np.array([1, 0, 0, 0, 0, 1, 0, 1])
        expected = np.array([0, 1, 2, 5, 6, 7])

        actual = evaluation.fifty_fifty_split(np.array(labels))
        assert_array_equal(expected, actual)


    @raises(ValueError)
    def test_no_0(self):
        labels = np.array([1, 1, 1, 1, 1, 1, 1, 1])
        evaluation.fifty_fifty_split(np.array(labels))

    @raises(ValueError)
    def test_no_1(self):
        labels = np.array([0, 0, 0, 0, 0, 0, 0, 0])
        evaluation.fifty_fifty_split(np.array(labels))