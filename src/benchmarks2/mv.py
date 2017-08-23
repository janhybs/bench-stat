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


class MV(IBenchmark):

    def __init__(self, n, pargs):
        """
        :type n: int
        :type pargs: utils.parser.ParseResult
        """
        super(MV, self).__init__(
            'bench-mv-%d' % n,
            'Matrix vector multiply', n)

        self.pargs = pargs
        self.rows = int(round(ease(n, 10**1, 10**5, 'easeInExpoConfig')))
        self.cols = self.rows
        self.matrix = None      # type: csr_matrix
        self.vector = None      # type: csr_matrix
        self.size = self.rows
        self.reps = 100

    def setup(self):
        matrix_a_coo = generate_sparse_matrix(
            self.rows,
            int(30 * self.pargs.per_line_factor),
            int(50 * self.pargs.bandwidth_factor),
        )
        self.matrix = matrix_a_coo.tocsr()
        self.vector = np.random.random(self.rows)

    def test(self, *args, **kwargs):
        self.result = self.matrix.dot(self.vector)

    def breakdown(self):
        self.matrix = None
        self.vector = None
        self.result = None

    @property
    def detail(self):
        return 'A({}x{}) B({})'.format(self.rows, self.rows, self.rows)


# plt.matshow(result)
# # plt.matshow(result)
# sns.heatmap(result)
# plt.show()