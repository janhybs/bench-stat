#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import json
import random
import codecs
from benchmarks._generator import TestGenerator
from utils.parser import parse_args
from utils import strings
import subprocess
import uuid
import os
import sys
from importlib import util as importlib
import collect_data

collect_data_path = importlib.find_spec('collect_data').loader.path
executable_path = sys.executable
debug_mode = 1


script = '''
#!/bin/bash

export LC_ALL=C

/usr/bin/time -f '{{"real": %e, "user": %U, "sys": %S}}' \\
    -o {time_filename} \\
        {command} \\
        -o {result_filename}

{executable_path} {collect_data_path} \\
    --mpstat "{mpstat_filename}" \\
    --time "{time_filename}" \\
    --result "{result_filename}" \\
    --rest "{pass_args}"

'''.strip()

args = parse_args()
generator = TestGenerator(args)


def execute_no_pbs(t):
    t.execute()


def execute_no_qsub(t, pass_args=''):
    return execute_benchmark(t, False, pass_args)


def execute_qsub(t, pass_args=''):
    return execute_benchmark(t, True, pass_args)


def execute_benchmark(t, use_qsub, pass_args):
    rnd = '%s-%d' % (uuid.uuid4().hex, random.randint(1000, 9999))
    command = ' '.join(t.command_line)
    filename = os.path.abspath('%s-%d-%s' % (t.family, t.n, rnd))
    shell_filename = filename + '.sh'
    time_filename = filename + '.time.json'
    mpstat_filename = filename + '.mpstat.txt'
    result_filename = filename + '.result.json'

    args = locals().copy()
    args.update(globals())
    content = script.format(**args)

    with open(shell_filename, 'w') as fp:
        fp.write(content)
    os.chmod(shell_filename, 0o777)

    if use_qsub:
        process = subprocess.Popen(['qsub', shell_filename])
    else:
        process = subprocess.Popen([shell_filename])
        collect_command = '-m {mpstat_filename} -t {time_filename} -r {result_filename} --rest "{pass_args}"'.format(
            **locals()).split()
        return process, collect_command, shell_filename


for r in range(args.reps):
    print('Repetition %d of %d' % (r+1, args.reps))

    for t in generator.selected_tests:
        count = 2
        rnd = '%s-%d' % (uuid.uuid4().hex, random.randint(1000, 9999))
        ps = list()

        for i in range(count):
            data = dict(
                type='normal',
                child=chr(65+i),
                family=rnd,
            )
            ps.append(execute_no_qsub(t, pass_args=strings.obj2base64(data)))

        for p0, c0, sh in ps:
            p0.wait()
            os.unlink(sh)

        # for p0, c0, sh in ps:
        #     collect_data.main(c0)

