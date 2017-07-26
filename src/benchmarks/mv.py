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
import numpy as np
from matplotlib import pyplot as plt


class MV(IBenchmark):

    @staticmethod
    def create(n, a_cfg, b_cfg):
        """
        Creates instance of Benchmark
        performing sparse matrix sparse vector multiplication
        :type a_cfg: mc
        :type b_cfg: vc
        """
        return MV(n, a_cfg, b_cfg)

    def __init__(self, n, a_cfg, b_cfg):
        super(MV, self).__init__(
            'bench-mv-%d' % n,
            'Sparse matrix sparse vector multiplication', n
        )

        self.a_cfg = a_cfg      # type: mc
        self.b_cfg = b_cfg      # type: vc
        self.matrix = None      # type: csr_matrix
        self.vector = None      # type: np.ndarray

    def setup(self):
        self.matrix = mg.generate_matrix(self.a_cfg)
        self.vector = mg.generate_vector(self.b_cfg)

    def test(self, *args, **kwargs):
        self.result = self.matrix.dot(self.vector)

    @property
    def detail(self):
        return 'A({}x{}) b({})'.format(self.a_cfg.rows, self.a_cfg.cols, self.b_cfg.size)
