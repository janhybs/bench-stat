#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

"""
Benchmark test which performs sparse matrix x vector multiplication
"""
from scipy.sparse import coo_matrix
from scipy.sparse.csr import csr_matrix

from benchmarks import IBenchmark
from benchmarks import MatrixConfiguration as mc

import pandas as pd
import numpy as np


class MA2(IBenchmark):

    @staticmethod
    def create(n, a_cfg):
        """
        Creates instance of Benchmark
        performing matrix assembly
        :type a_cfg: mc
        """
        return MA2(n, a_cfg)

    def __init__(self, n, a_cfg):
        super(MA2, self).__init__(
            'bench-ma2-%d' % n,
            'Matrix assembly', n
        )

        self.a_cfg = a_cfg          # type: mc
        self.dense_matrix = None    # type: np.ndarray
        self.sparse_matrix = None   # type: np.ndarray

    def setup(self):
        self.dense_matrix = np.random.random(4 * 4)
        self.sparse_matrix = np.zeros(self.a_cfg.size)

    def test(self, *args, **kwargs):
        # lokalni pevna husta mala
        # matice coo

        limit = self.a_cfg.rows
        local_size = 4
        step = local_size * local_size
        items_size = (self.a_cfg.rows-local_size) * step
        rows_data = np.empty(items_size, dtype=np.int)
        cols_data = np.empty(items_size, dtype=np.int)
        data_data = np.ones(items_size, dtype=np.float)

        bw = self.a_cfg.bandwidth
        for i in range(self.a_cfg.rows-local_size):
            cols_data[i*step:(i+1)*step] = [i, i+1, i+np.sqrt(bw), i+bw]*local_size
            rows_data[i*step:(i+1)*step] = [i]*4 + [i+1]*4 + [i+2]*4 + [i+3]*4

            # print(rand_index)
        cols_data = np.mod(cols_data, limit)

        matrix = coo_matrix((data_data, (rows_data, cols_data)), shape=self.a_cfg.size, dtype=np.double)
        self.result = matrix.tocsr()
        # print(self.result.toarray())
        #
        # limit = self.a_cfg.rows
        # arr = np.empty((1, 4), dtype=np.int)
        # for i in self.a_cfg:
        #     arr[:] = np.mod([i, i+1, i+np.sqrt(bw).astype(int), i+bw], limit)
        #     self.sparse_matrix[arr, arr.T] += self.dense_matrix[arr, arr.T]
        # self.result = self.sparse_matrix
        # to csr

    @property
    def detail(self):
        return 'A({}x{})'.format(self.a_cfg.rows, self.a_cfg.cols)