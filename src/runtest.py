#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import time

print('!!!!!!!!!!!')
time.sleep(1)

from benchmarks2 import TestGenerator
from utils.parser import parse_args

pargs = parse_args()
tests = TestGenerator.generate_tests(pargs)

if len(tests) != 1:
    raise Exception('Given arguments must specify single test')

test = tests[0]   # IBenchmark


print(test.execute())
print(test.json_result)

if pargs.output:
    import json
    print(pargs.output)
    with open(pargs.output, 'w') as fp:
        json.dump(test.json_result, fp)

