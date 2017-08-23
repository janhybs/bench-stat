#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs
from benchmarks2 import IBenchmark
from benchmarks2 import np
from benchmarks2 import coo_matrix
from utils.easing import ease


class MA(IBenchmark):
    def __init__(self, n, pargs, **kwargs):
        """
        :type n: int
        :type pargs: utils.parser.ParseResult
        """
        super(MA, self).__init__(
            'bench-ma-%d' % n,
            'Matrix assembly', n)

        self.rows = int(round(ease(n, 10**1, 10**5, 'easeInExpoConfig')))
        self.cols = self.rows
        self.bandwidth = int(50 + pargs.bandwidth_factor)
        self.per_line = 10

        self.dense_matrix = None
        self.reps = 1
        self.size = self.rows

    def setup(self):
        self.dense_matrix = np.random.random(4 * 4)

    def test(self, *args, **kwargs):
        local_size = 4
        step = local_size * local_size
        items_size = (self.rows - local_size) * step
        rows_data = np.empty(items_size, dtype=np.int)
        cols_data = np.empty(items_size, dtype=np.int)
        data_data = np.ones(items_size, dtype=np.float)

        bw = self.bandwidth
        for i in range(self.rows - local_size):
            cols_data[i * step:(i + 1) * step] = [i, i + 1, i + np.sqrt(bw), i + bw] * local_size
            rows_data[i * step:(i + 1) * step] = [i] * 4 + [i + 1] * 4 + [i + 2] * 4 + [i + 3] * 4

        cols_data = np.mod(cols_data, self.rows)

        matrix = coo_matrix((data_data, (rows_data, cols_data)), shape=(self.rows, self.cols), dtype=np.double)
        self.result = matrix.tocsr()

    def breakdown(self):
        self.result = None
        self.dense_matrix = None

    @property
    def detail(self):
        return 'A({}x{})'.format(self.rows, self.cols)