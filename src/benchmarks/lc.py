#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

from scipy.sparse.csr import csr_matrix

from benchmarks import IBenchmark
from benchmarks import VectorConfiguration as vc

import pandas as pd
import numpy as np


class LC(IBenchmark):

    @staticmethod
    def create(n, size, count):
        """
        Creates instance of Benchmark
        performing linear combination operation
        :type size: int
        :type count: int
        """
        return LC(n, size, count)

    def __init__(self, n, size, count):
        super(LC, self).__init__(
            'bench-lc-%d' % n,
            'Linear combination of vectors', n
        )

        self.size = size        # type: int
        self.count = count      # type: int
        self.vectors = None     # type: np.ndarray
        self.coefs = None       # type: np.ndarray

    def setup(self):
        self.vectors = np.random.random((self.size, self.count))
        self.coefs = np.random.random((self.count, 1))

    def test(self, *args, **kwargs):
        self.result = self.vectors.dot(self.coefs)

    @property
    def detail(self):
        return 'A({}x{}) b({})'.format(self.count, self.size, self.size)
