#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import sys
import threading
import time
from importlib import util as importlib


# import numpy as np
# import pandas as pd
# from scipy.sparse.coo import coo_matrix
# from scipy.sparse.csr import csr_matrix
#
# pd.set_option("max_rows", 200)
# pd.set_option("max_columns", 200)
# pd.set_option("max_colwidth", 200)
# pd.set_option("display.width", 200)
#
# np.random.seed(1234)


def print_section(value, left=10, right=70, fill='-'):
    # print('-' * (left + right))
    print(('{:%s>%ds}{:%s<%ds}' % (fill, left, fill, right)).format('', ' %s ' % value))
    # print('-' * (left + right))


class measure(object):
    def __init__(self, start_msg, end_msg=None, fill='-',):
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
    runtest = importlib.find_spec('runtest')

    def __init__(self, name, description, n):
        super(IBenchmark, self).__init__(name=name)
        self.name = name
        self.description = description
        self._reps = 1

        self.run_measure = None     # type: measure
        self.setup_measure = None   # type: measure
        self.test_measure = None    # type: measure
        self.result = None          # type: np.ndarray
        self.n = n
        self.json_result = None
        self.family = self.__class__.__name__.lower()

    def repeat(self, count):
        self.reps = count
        return self

    @classmethod
    def generate(cls, N, pargs, *args, **kwargs):
        print(cls())

    @property
    def duration(self):
        return self.test_measure.duration

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
    def command_line(self):
        return [
            sys.executable,
            self.runtest.loader.path,
            '-t', '%s:%d' % (self.family, self.n)
        ]

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
        print()
        self.json_result = dict()
        self.json_result['name'] = self.name
        self.json_result['duration'] = self.duration

    def __call__(self, *args, **kwargs):
        self.execute()
        # from matplotlib import pyplot as plt
        # plt.matshow(self.result.toarray())
        # plt.show()
        return self


class MatrixConfiguration(object):

    def __init__(self, rows=None, cols=None, per_line=None, bandwidth=None, square=None):
        if square is not None:
            self.rows = square
            self.cols = square
        else:
            self.rows = rows
            self.cols = cols or rows

        self.per_line = per_line
        self.bandwidth = bandwidth

    @property
    def size(self):
        return self.rows, self.cols

    @property
    def rows_range(self):
        return range(self.rows)

    @property
    def cols_range(self):
        return range(self.cols)

    def __iter__(self):
        return iter(range(self.rows))


class VectorConfiguration(object):
    def __init__(self, size):
        self.size = size


class MatrixConstructor(object):

    @staticmethod
    def generate_matrix(cfg):
        """
        :rtype: csr_matrix
        :type cfg: MatrixConfiguration
        """
        import numpy as np
        from scipy.sparse.coo import coo_matrix

        # matrix = coo_matrix(cfg.size, dtype=np.double)

        bw = cfg.bandwidth
        pl = cfg.per_line
        rows, cols = cfg.rows, cfg.cols
        middle = False
        per_line = pl * 2 + 1

        rows_data = np.empty(per_line * rows, dtype=np.int)
        cols_data = np.empty(per_line * rows, dtype=np.int)
        data_data = np.ones(per_line * rows, dtype=np.float)

        for row in range(cfg.rows):
            # diagonal
            # matrix[row, row] = 1.0

            if row-1 < bw:
                extra_bw = bw - row
                extra_pl = int((extra_bw / bw) * pl)
                # left_space = range(1, row + 1)
                # right_space = range(1, 1 + bw + extra_bw)
                left_space = np.linspace(1, row + 1, pl - extra_pl, False,  dtype=np.int)
                right_space = np.linspace(1, 1 + bw + extra_bw, pl + extra_pl, False, dtype=np.int)
            elif row-1 >= bw and row < rows-bw:
                if not middle:
                    left_space = np.linspace(1, 1 + bw, pl, False, dtype=np.int)
                    right_space = left_space
                    middle = True
                # left_space = right_space = range(1, 1 + bw)
            else:
                extra_bw = ((row+1) + bw) - cols
                extra_pl = int((extra_bw / bw) * pl)
                left_space = np.linspace(1, 1 + bw + extra_bw, pl + extra_pl, False, dtype=np.int)
                right_space = np.linspace(1, 1 + bw - extra_bw, pl - extra_pl, False, dtype=np.int)
                # left_space = range(1, 1 + bw + extra_bw)
                # right_space = range(1, 1 + bw - extra_bw)

            # matrix[row, row - left_space] = 1
            # matrix[row, row + right_space] = 1

            rows_data[row * per_line:(row + 1) * per_line] = row
            cols_data[row * per_line:(row + 1) * per_line] = np.hstack((left_space, [row], right_space))

        matrix = coo_matrix((data_data, (rows_data, cols_data)), shape=(rows, cols), dtype=np.double)
        return matrix.tocsr()

    @staticmethod
    def generate_vector(cfg):
        """
        :rtype: csr_matrix
        :type cfg: VectorConfiguration
        """
        import numpy as np
        return np.random.random(cfg.size)


