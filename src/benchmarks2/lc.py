#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

from benchmarks2 import IBenchmark
from benchmarks2 import np
from utils.easing import ease


class LC(IBenchmark):

    def __init__(self, n, pargs, **kwargs):
        """
        :type n: int
        :type pargs: utils.parser.ParseResult
        """
        super(LC, self).__init__(
            'bench-lc-%d' % n,
            'Linear combination', n)

        self.size = int(round(ease(n, 10**1, 10**5, 'easeInExpo'))) # type: int
        self.count = int(10 + pargs.lc_count)                       # type: int
        self.vectors = None                                         # type: np.ndarray
        self.coefs = None                                           # type: np.ndarray
        self.rows = self.size
        self.reps = 5000

    def setup(self):
        self.vectors = np.random.random((self.count, self.size))
        self.coefs = np.random.random((self.size, 1))

        # self.vectors = np.ones((self.count, self.size))
        # self.coefs = np.ones((self.size, 1))

    def test(self, *args, **kwargs):
        self.result = self.vectors.dot(self.coefs)

    def breakdown(self):
        self.vectors = None
        self.coefs = None
        self.result = None

    @property
    def detail(self):
        return 'A({}x{}) b({})'.format(self.count, self.size, self.size)
