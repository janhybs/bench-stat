#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs
from benchmarks import IBenchmark


# all test are working variable n which represents task size
# variable n affects all tests
# variable ranges from 1 - 10
class TestGenerator(object):
    tests = ['LC', 'MA', 'MA2', 'MM', 'MS', 'MV', 'SV']
    default_N = 1, 2, 3, 4

    def __init__(self, args=None):
        """
        :type args: utils.parser.ParseResult
        """
        self.args = args
        self._all_tests = None
        self._selected_tests = None

    @property
    def selected_tests(self):
        """
        :rtype: list[IBenchmark]
        """
        if not self._selected_tests:
            self._selected_tests = TestPool()
            for test_cfg in self.args.tests:
                cfg = test_cfg.split(':')
                if len(cfg) == 1:
                    print('aaa')
                else:
                    print(cfg)
                    from benchmarks.ma2 import MA2
                    print(MA2.generate(0, 0))
                #     self._selected_tests.extend(
                #         self.all_tests.get_tests('bench', *cfg)
                #     )
                # else:
                #     self._selected_tests.append(
                #         self.all_tests.get_test('bench', *cfg)
                #     )
        return self._selected_tests

    @property
    def all_tests(self):
        if not self._all_tests:
            self._all_tests = self.prepare_all()
        return self._all_tests

    def prepare_all(self, N=default_N):
        all_tests = TestPool()

        for i in self.tests:
            all_tests.extend(
                getattr(self, 'generate_%s' % i.lower())(*N)
            )
        return all_tests

    def generate_ms(self, *N):
        from benchmarks.ms import MS
        items = list()
        for n in N:
            items.append(
                MS.create(n,
                    rows=8 + self.args.ms_count,     # zmena velikosti male matice
                    count=2 ** (11 + n)              # pocet opakovani velke n
                ))
            # items[-1].reps = 44 - n*10
        return items

    def generate_lc(self, *N):
        from benchmarks.lc import LC

        items = list()
        for n in N:#2**10, 2**13, 2**15, 2**17:
            items.append(
                LC.create(n,
                    size=2**(12 + n),
                    count=1000 + self.args.lc_count
                ))
            items[-1].reps = 10     # to increase duration
        return items

    def generate_ma(self, *N):
        from benchmarks.ma import MA
        from benchmarks import MatrixConfiguration as mc

        items = list()
        for n in N:
            items.append(
                MA.create(n, mc(
                    square=n*100,
                    per_line=10,
                    bandwidth=50 + self.args.bandwidth_factor
                )).repeat(2000))
        return items

    def generate_ma2(self, *N):
        from benchmarks.ma2 import MA2
        from benchmarks import MatrixConfiguration as mc

        items = list()
        for n in N:
            items.append(
                MA2.create(n, mc(
                    square=n*100,
                    per_line=10,
                    bandwidth=50 + self.args.bandwidth_factor
                )).repeat(2000))
        exit(0)
        return items

    def generate_mm(self, *N):
        from benchmarks.mm import MM
        from benchmarks import MatrixConfiguration as mc

        items = list()
        for n in N:#2**10, 2**12, 2**14, 2**16:
            items.append(
                MM.create(n, mc(
                    square=2 ** (8 + 2*n),
                    per_line=30,
                    bandwidth=50
                ), mc(
                    square=2 ** (8 + 2*n),
                    per_line=30,
                    bandwidth=50
                )))
        return items

    def generate_mv(self, *N):
        from benchmarks.mv import MV
        from benchmarks import MatrixConfiguration as mc
        from benchmarks import VectorConfiguration as vc

        items = list()
        for n in N:#2**10, 2**13, 2**15, 2**17:
            items.append(
                MV.create(n, mc(
                    rows=2 ** (10 + 2*n),
                    per_line=30,
                    bandwidth=50
                ),vc(
                    size=2 ** (10 + 2*n),
                )))
        return items

    def generate_sv(self, *N):
        from benchmarks.sv import SV

        items = list()
        for n in N:
            items.append(
                SV.create(n,
                    count=2 ** (14 +n),
                    slow_down_func=SV.generate_slow_down(self.args.sv_slow)
                ))
        return items


class TestPool(list):
    """
    Class TestPool
     :type : list[IBenchmark]
    """

    def __init__(self):
        super(TestPool, self).__init__()

    def get_test(self, *args):
        name = '-'.join([str(x) for x in args]).lower()
        for t in self:
            if t.name == name:
                return t
        return None

    def get_tests(self, *args):
        name = '-'.join([str(x) for x in args]).lower()
        return [t for t in self if str(t.name).startswith(name)]