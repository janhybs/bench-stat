#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

"""
Benchmark test which performs sparse matrix x vector multiplication
"""
from scipy.sparse.csr import csr_matrix

from benchmarks import IBenchmark
from benchmarks import MatrixConfiguration as mc
from benchmarks import VectorConfiguration as vc
from benchmarks import MatrixConstructor as mg
import pandas as pd



class MM(IBenchmark):

    @staticmethod
    def create(n, a_cfg, b_cfg):
        """
        Creates instance of Benchmark
        performing sparse matrix multiplication
        :type a_cfg: mc
        :type b_cfg: mc
        """
        return MM(n, a_cfg, b_cfg)

    def __init__(self, n, a_cfg, b_cfg):
        super(MM, self).__init__(
            'bench-mm-%d' % n,
            'Sparse matrix sparse matrix multiplication', n
        )

        self.a_cfg = a_cfg      # type: mc
        self.b_cfg = b_cfg      # type: mc
        self.matrix_a = None      # type: csr_matrix
        self.matrix_b = None      # type: csr_matrix

    def setup(self):
        self.matrix_a = mg.generate_matrix(self.a_cfg)
        self.matrix_b = mg.generate_matrix(self.b_cfg)

    def test(self, *args, **kwargs):
        self.result = self.matrix_a.dot(self.matrix_b)

    @property
    def detail(self):
        return 'A({}x{}) B({}x{})'.format(self.a_cfg.rows, self.a_cfg.cols, self.b_cfg.rows, self.b_cfg.cols)
