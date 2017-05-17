#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

from os.path import join, realpath, dirname

__dir__ = realpath(dirname(__file__))
__root__ = realpath(join(__dir__, '../'))

from argparse import ArgumentParser
import subprocess
import sys
import os
import time


parser = ArgumentParser()

parser.add_argument('-t', '--test-id')
parser.add_argument('-r', '--rep-id')
parser.add_argument('-c', '--commit')

args = parser.parse_args()


def execute(command, **kwargs):
    print('$>', ' '.join(command))
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, **kwargs).decode()
    for line in output.splitlines():
        print(' '*3, line)


git_clone = ['git', 'clone', 'https://github.com/x3mSpeedy/bench-stat.git', 'repo']
execute(git_clone)

git_checkout = ['git', 'checkout', '--force', args.commit]
execute(git_checkout, cwd='repo')

git_branch = ['git', 'branch']
execute(git_branch, cwd='repo')


# read version from cloned repo
version = open(join('repo', 'version')).read().strip()

__bench__ = realpath('repo/benchmarks')
make_compile = ['make', 'compile']
execute(make_compile, cwd=__bench__)


result_json = realpath('result.json')
binary = realpath(join(__bench__, 'O3.out'))
run_test = [binary, result_json, version, str(args.test_id)]
execute(run_test, cwd=__bench__)