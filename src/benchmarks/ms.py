#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

from scipy.sparse.csr import csr_matrix

from benchmarks import IBenchmark
from benchmarks import MatrixConfiguration as mc

import pandas as pd
import numpy as np


class MS(IBenchmark):

    @staticmethod
    def create(n, rows, count):
        """
        Creates instance of Benchmark
        performing matrix simple operations
        :type rows: int
        :type count: int
        """
        return MS(n, rows, count)

    def __init__(self, n, rows, count):
        super(MS, self).__init__(
            'bench-ms-%d' % n,
            'Matrix simple operations', n
        )

        self.rows = rows            # type: int
        self.cols = rows            # type: int
        self.count = count          # type: int
        self.dense_matrix = None    # type: np.ndarray
        self.sparse_matrix = None   # type: np.ndarray
        self.mult_matrix = None     # type: np.ndarray
        self.imult_matrix = None    # type: np.ndarray

    def setup(self):
        self.dense_matrix = np.random.random((self.rows, self.cols))
        self.mult_matrix = np.random.random((self.rows, self.cols))
        self.imult_matrix = np.linalg.inv(self.mult_matrix)

    def test(self, *args, **kwargs):
        count = self.count
        matrix = self.dense_matrix

        for i in range(count):
            # matrix += 1.0
            # matrix -= 1.0
            #
            # matrix *= 2.0
            # matrix /= 2.0
            matrix = matrix.dot(self.mult_matrix)
            matrix = matrix.dot(self.imult_matrix)
            matrix = np.linalg.inv(matrix)
            matrix = np.linalg.inv(matrix)
            pass
            # inverze (do 16)
            # maticove nasobeni
        self.result = matrix

    @property
    def detail(self):
        return 'A({}x{}) x {}'.format(self.rows, self.cols, self.count)