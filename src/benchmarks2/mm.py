#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

"""
Benchmark test which performs sparse matrix x vector multiplication
"""
from benchmarks2 import IBenchmark
from benchmarks2 import np
from benchmarks2 import coo_matrix
from benchmarks2 import csr_matrix
from benchmarks2 import sns, plt
from benchmarks2 import generate_sparse_matrix
from utils.easing import ease
import gc

class MM(IBenchmark):

    def __init__(self, n, pargs):
        """
        :type n: int
        :type pargs: utils.parser.ParseResult
        """
        super(MM, self).__init__(
            'bench-mm-%d' % n,
            'Matrix matrix multiply', n)

        self.pargs = pargs
        self.rows = int(round(ease(n, 10**1, 10**5, 'linear')))
        self.cols = self.rows
        self.matrix_a = None      # type: csr_matrix
        self.matrix_b = None      # type: csr_matrix
        self.size = self.rows

    def setup(self):

        matrix_a_coo = generate_sparse_matrix(
            self.rows,
            int(30 * self.pargs.per_line_factor),
            int(50 * self.pargs.bandwidth_factor),
        )
        self.matrix_a = matrix_a_coo.tocsr()

        matrix_b_coo = generate_sparse_matrix(
            self.rows,
            int(30 * self.pargs.per_line_factor),
            int(50 * self.pargs.bandwidth_factor),
        )
        self.matrix_b = matrix_b_coo.tocsr()

    def test(self, *args, **kwargs):
        self.result = self.matrix_a.dot(self.matrix_b)

    def breakdown(self):
        self.matrix_a = None
        self.matrix_b = None
        self.result = None

    @property
    def detail(self):
        return 'A({}x{}) B({}x{})'.format(self.rows, self.cols, self.rows, self.cols)


# plt.matshow(result)
# # plt.matshow(result)
# sns.heatmap(result)
# plt.show()