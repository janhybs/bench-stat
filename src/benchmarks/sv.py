#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

"""
Benchmark test which performs sparse matrix x vector multiplication
"""
from scipy.sparse.csr import csr_matrix

from benchmarks import IBenchmark
from benchmarks import MatrixConfiguration as mc

import random
import pandas as pd
import numpy as np


class SV(IBenchmark):

    @staticmethod
    def generate_slow_down(factor=None):
        if not factor:
            return None

        lst = list(range(factor))

        def slow_down_func(x):
            return x + sum(lst)

        return slow_down_func

    @staticmethod
    def create(n, count, slow_down_func):
        """
        Creates instance of Benchmark
        performing array sorting
        :type count: int
        :type slow_down_func: callable
        """
        return SV(n, count, slow_down_func)

    def __init__(self, n, count, slow_down_func):
        super(SV, self).__init__(
            'bench-sv-%d' % n,
            'Array sort', n
        )

        self.slow_down = slow_down_func     # type: callable
        self.count = count                  # type: int
        self.items = None                   # type: list

    def setup(self):
        # self.items = np.array([random.randint(0, self.count) for x in range(self.count)])
        self.items = [random.randint(0, self.count) for x in range(self.count)]

    def test(self, *args, **kwargs):
        self.result = sorted(self.items, key=self.slow_down)
        # self.result = np.sort(self.items)

    @property
    def detail(self):
        return 'a({})'.format(self.count)

