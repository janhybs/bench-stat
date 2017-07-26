#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs
import getpass
import random
from os.path import join, realpath, dirname

from db.mongo import Mongo

__dir__ = realpath(dirname(__file__))
__root__ = realpath(join(__dir__, '../'))

from argparse import ArgumentParser
import subprocess
import sys
import os
import time
import json
import platform
import numpy as np


parser = ArgumentParser()

parser.add_argument('-t', '--test-id', type=int)
parser.add_argument('-r', '--rep-id', type=int)
parser.add_argument('-c', '--commit', type=str)

args = parser.parse_args()


def execute(command, **kwargs):
    print('$>', ' '.join(command))
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, **kwargs).decode()
    for line in output.splitlines():
        print(' '*3, line)


# git_clone = ['git', 'clone', 'https://github.com/x3mSpeedy/bench-stat.git', 'repo']
# execute(git_clone)
#
# git_checkout = ['git', 'checkout', '--force', args.commit]
# execute(git_checkout, cwd='repo')
#
# git_branch = ['git', 'branch']
# execute(git_branch, cwd='repo')
#
#
# # read version from newly cloned repo
# version = open(join('repo', 'version')).read().strip()
#
# __bench__ = realpath('repo/benchmarks')
# make_compile = ['make', 'compile']
# execute(make_compile, cwd=__bench__)

# # execute test
# result_json = realpath('result.json')
# binary = realpath(join(__bench__, 'O3.out'))
# run_test = [binary, result_json, version, str(args.test_id)]
# execute(run_test, cwd=__bench__)

# extract user and machine info
choices = ['tarkil', 'luna', 'mudrc', 'alfrid', 'janhybs', 'foo', 'bar']
probs   = [1, 100, 20, 30, 10, 2, 1]
restrictions = os.environ['RESTRICTIONS'][1:].split(':')

print(restrictions)
for r in restrictions:
    if r:
        name = str(r).split('_')[1].split('=')[0]
        index = choices.index(name)
        print(index)
        del choices[index]
        del probs[index]


probs = np.array(probs)
choice = np.random.choice(choices, p=probs/probs.sum())
print(choice)

hostname = str(platform.node())                             # full name such as mudrc7.cesnet.cz
hostname = choice
nodename = str(hostname.split('.')[0]).strip('0123456789')  # short name such as mudrc
username = str(getpass.getuser())
version = '1.0.0'

# with open(result_json, 'r') as fp:
#     data_json = json.load(fp)   # type: dict
#

data_json = {
    'n-' + str(args.test_id): {
        'duration': 0.5
    },
    'version': None
}

data_json.pop('version')
keys = list(data_json.keys())
if len(keys) > 1:
    raise Exception('Invalid json format')


# transform results
data = dict(
    version=version,
    username=username,
    nodename=nodename,
    hostname=hostname,
    rep_id=args.rep_id,
    test_id=args.test_id,
    commit=args.commit,
    test_name=keys[0],
    duration=data_json[keys[0]]['duration'],
)

mongo = Mongo()
mongo.bench_new.insert_one(data)
