#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import importlib
from importlib import util
import threading
import time
import sys

import numpy as np
import seaborn as sns

from matplotlib import pyplot as plt
from scipy.sparse.csr import csr_matrix
from scipy.sparse.coo import coo_matrix


def generate_sparse_matrix(n, pl, bw):
    per_line = pl * 2 + 1
    rows_data = np.empty(per_line * n, dtype=np.int)
    cols_data = np.empty(per_line * n, dtype=np.int)
    data_data = np.ones(per_line * n, dtype=np.float)

    pl1 = pl + 1
    pts = np.linspace(1, 1 + bw, pl, False, dtype=np.int) - 1

    for i in range(n):
        rs = i + pts
        rs[(rs >= n)] = i

        ls = i - pts
        ls[(ls < 0)] = i

        s = i * per_line
        cols_data[s:s+pl] = ls
        cols_data[s+pl] = i
        cols_data[s+pl1:s+per_line] = rs
        # cols_data[i * per_line:(i+1) * per_line] = np.hstack((ls, [i], rs))

        rows_data[s:(i + 1) * per_line] = i

    matrix = coo_matrix((data_data, (rows_data, cols_data)), shape=(n, n), dtype=np.double)
    return matrix

# t = time.time()
# generate_sparse_matrix(10**5, 30, 50)
# print(time.time() - t)
#
# t = time.time()
# generate_sparse_matrix(10**5, 30, 50).tocsr()
# print(time.time() - t)
#
# result = generate_sparse_matrix(100, 30, 50).toarray()
#
# # plt.matshow(result)
# # # plt.matshow(result)
# sns.heatmap(result)
# plt.show()
# exit(0)


def print_section(value, left=10, right=70, fill='-'):
    # print('-' * (left + right))
    print(('{:%s>%ds}{:%s<%ds}' % (fill, left, fill, right)).format('', ' %s ' % value))
    # print('-' * (left + right))


class TestGenerator(object):
    @classmethod
    def generate_test(cls, name, N, pargs=None, **kwargs):
        c = getattr(importlib.import_module('benchmarks2.%s' % name.lower()), name.upper())
        return c(N, pargs, **kwargs)

    @classmethod
    def generate_tests(cls, pargs):
        """
        :type pargs: utils.parser.ParseResult
        """
        tests = list()
        if pargs.tests:
            for test_name, N in pargs.tests:
                if N is None:
                    for i in range(0, 101, 2):
                        tests.append(cls.generate_test(test_name, i, pargs))
                else:
                    tests.append(cls.generate_test(test_name, N, pargs))
        return tests


class measure(object):
    def __init__(self, start_msg, end_msg=None, fill='-'):
        self.start_msg = start_msg
        self.end_msg = end_msg
        self.fill = fill

        self.start_time = None
        self.end_time = None

    @property
    def duration(self):
        return self.end_time - self.start_time

    def __enter__(self):
        if self.start_msg:
            print_section(self.start_msg.format(self=self), fill=self.fill)

        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()

        if self.end_msg:
            print_section(self.end_msg.format(self=self), fill=self.fill)
        return False


class IBenchmark(threading.Thread):
    runtest = util.find_spec('runtest')

    def __init__(self, name, description, n):
        super(IBenchmark, self).__init__(name=name)
        self.name = name                # type: str
        self.description = description  # type: str
        self.n = n                      # type: int

        self.run_measure = None         # type: measure
        self.setup_measure = None       # type: measure
        self.test_measure = None        # type: measure
        self.result = None              # type: np.ndarray

        self.json_result = None         # type: dict
        self.family = self.__class__.__name__.lower()

        self._reps = 1                  # type: int

    def __call__(self, *args, **kwargs):
        self.execute()
        return self

    @property
    def test_id(self):
        return '%s:%d' % (self.family, self.n)

    @property
    def command_line(self):
        return [
            sys.executable,
            self.runtest.loader.path,
            '-t', self.test_id
        ]

    @property
    def detail(self):
        return ''

    @property
    def reps(self):
        return self._reps

    @reps.setter
    def reps(self, value):
        self._reps = max(1, value)

    @property
    def duration(self):
        return self.test_measure.duration

    def execute(self):
        self.start()
        self.join()
        return self

    def setup(self):
        """
        Method will prepare test
        """
        pass

    def breakdown(self):
        """
        Method will end test process freeing resources etc.
        """
        pass

    def test(self, *args, **kwargs):
        """
        Method will execute test
        :return:
        """
        pass

    def run(self):
        with measure('%s %s' % (self.name, self.detail), fill='=') as self.run_measure:
            with measure('setting up', 'data generated  ({self.duration:1.5f} sec)') as self.setup_measure:
                result = self.setup()

            # print()
            with measure('starting benchmark', 'benchmark ended ({self.duration:1.5f} sec)') as self.test_measure:
                for i in range(self.reps):
                    self.test(result)

        self.breakdown()

        print()
        self.json_result = dict()
        self.json_result['name'] = self.name
        self.json_result['duration'] = self.duration
        self.json_result['reps'] = self.reps
        self.json_result['n'] = self.n
        self.json_result['size'] = getattr(self, 'size', getattr(self, 'rows', self.n))