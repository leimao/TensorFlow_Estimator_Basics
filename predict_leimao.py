"""Predict using estimator.predict"""

__author__ = "Guillaume Genthial"


import functools
from pathlib import Path
import logging
import sys
import time

import tensorflow as tf

from model import model_fn


def example_input_fn(number):
    """Dummy input_fn"""
    dataset = tf.data.Dataset.from_generator(
        lambda: ([number, number] for _ in range(1)),
        output_types=tf.float32, output_shapes=(2,))
    iterator = dataset.batch(1).make_one_shot_iterator()
    next_element = iterator.get_next()
    return next_element, None


def my_service():
    """Some service yielding numbers"""
    start, end = 100, 110
    for number in range(start, end):
        yield number


class TFEstimatorServe(object):

    def __init__(self, estimator):
        self.data = []
        self.estimator = estimator
        self.results = self.estimator.predict(input_fn=self.input_fn)
    
    def data_gen(self):

        while True:
            data = self.data.pop(0)
            yield data, data

    def input_fn(self):

        dataset = tf.data.Dataset.from_generator(self.data_gen, output_types=tf.float32, output_shapes=(2,))
        iterator = dataset.batch(1).make_one_shot_iterator()
        next_element = iterator.get_next()

        #print("---------------")
        #print(next_element)
        #print("---------------")
        return next_element
        #return next_element, None
        #return dataset

    def predict(self, data):

        self.data = data
        predictions = []
        for _ in range(len(data)):
            # print(next(self.results))
            predictions.append(next(self.results))
        return predictions


if __name__ == '__main__':
    '''
    # Logging
    Path('model').mkdir(exist_ok=True)
    tf.logging.set_verbosity(logging.INFO)
    handlers = [
        logging.FileHandler('model/predict.log'),
        logging.StreamHandler(sys.stdout)
    ]
    logging.getLogger('tensorflow').handlers = handlers
    '''

    # Instantiate estimator
    estimator = tf.estimator.Estimator(model_fn=model_fn, model_dir='model',
                                       params={})
    
    server = TFEstimatorServe(estimator=estimator)

    server.predict(data=[1])

    # Predict using the estimator
    tic = time.time()
    for nb in my_service():
        pred = server.predict(data=[nb])
        pred = pred[0]

        #print("------------------")
        #print((pred - 2*nb)**2)
        #print("------------------")
        

    toc = time.time()
    print('Average time in predict.py: {}s'.format((toc - tic) / 10))
