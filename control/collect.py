#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

from os.path import join, realpath
import yaml
import progressbar
import time
import sys
import datetime
import subprocess
import uuid
import platform

__dir__ = realpath(__file__)
__root__ = realpath(join(__dir__, '../' * 2))
__bench__ = realpath(join(__root__, 'benchmarks'))


json_name = 'result.{}.{}.json'.format(platform.node(), uuid.uuid4().hex)
result_json = realpath(join(__root__, 'results', json_name))


# make_compile = ['make', 'compile']
# print(subprocess.check_call(make_compile, cwd=__bench__))
#
# make_test = ['make', 'JSON='+result_json, 'test-fast']
# print(subprocess.check_call(make_test, cwd=__bench__))


hostname = platform.node().split('.')[0]
nodename = hostname.strip('0123456789')
print(result_json)