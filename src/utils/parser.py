#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import argparse
from utils.config import Mode

class ParseResult(object):
    """
    Class ParseResult
    :type tests             : list[str]

    :type per_line_factor   : float
    :type bandwidth_factor  : float

    :type lc_count          : int
    :type sv_slow           : int
    :type ms_count          : int


    :type mode              : Mode
    """

    def __init__(self, parsed):
        self.tests = None

        if parsed.test:
            self.tests = [self._parse_test(x) for y in parsed.test for x in y]

        self.parsed = parsed
        self.per_line_factor = parsed.per_line_factor
        self.bandwidth_factor = parsed.bandwidth_factor

        self.lc_count = parsed.lc_count
        self.sv_slow = parsed.sv_slow
        self.ms_count = parsed.ms_count

        self.output = parsed.output
        self.reps = parsed.reps
        self.skip_db = parsed.skip_db
        self.mode = parsed.mode

    def __repr__(self):
        return repr(self.parsed)

    @staticmethod
    def _parse_test(name):
        cfg = name.upper().split(':')
        if len(cfg) == 1:
            return cfg[0], None
        return cfg[0], int(cfg[1])


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', type=str, nargs='+', action='append',
                        help="List of tests from following: [LC or MA or MM or MS or MS or SV]")
    parser.add_argument('--per-line-factor', '--pl', type=float, default=1.0,
                        help="Factor increasing number of elements per line for tests MV and MM")
    parser.add_argument('--bandwidth-factor', '--bw', type=float, default=1.0,
                        help="Factor increasing number of acceptable bandwidth for tests MV and MM")
    parser.add_argument('--lc-count', '--lcc', type=int, default=0,
                        help="Increases number of repetition for test LC")
    parser.add_argument('--sv-slow', '--svs', type=int, default=0,
                        help="Increases access time when sorting for test SV")
    parser.add_argument('--ms-count', '--msc', type=int, default=0,
                        help="Increases number of repetition for test MS")
    parser.add_argument('--output', '-o', type=str, help="Json output location")
    parser.add_argument('--mode', '-m', type=Mode.parse, choices=Mode.values(), default=Mode.LOCAL, help="Json output location")
    parser.add_argument('--reps', '-r', type=int, default=1, help="Number of repetitions")
    parser.add_argument('--skip-db', action='store_true', help="If set, result will not be pushed to db")

    return ParseResult(parser.parse_args(args))
