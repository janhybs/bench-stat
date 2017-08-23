#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs
import time

from benchmarks2 import TestGenerator
from utils.parser import parse_args
import subprocess
import uuid
import os
import sys
import json
from utils.config import Mode
from importlib import util as importlib
import collect_data

collect_data_path = importlib.find_spec('collect_data').loader.path

# from utils import textplot

# c0 = [1.0, 1.98, 0.99, 64.0, 74.75, 78.79, 62.0]
# c1 = [0.0, 0.99, 0.0, 14.14, 0.0, 70.71, 77.0]
# c3 = [0.0, 0.0, 4.95, 31.96, 100.0, 12.24, 58.42]
# c2 = [0.0, 0.0, 2.0, 56.0, 0.0, 9.0, 64.65]

# try:
#     textplot.plot2(
#         c0, c1, c2, c3,
#         c0, c1, c2, c3,
#         c0, c1, c2, c3,
#         c0, c1, c2, c3,
#     )
#     # textplot.plot2(c3, c0)#, c1, c2, c3)
# except:
#     raise
# exit(0)


# module load python34-modules-gcc
# qsub -l select=1:ncpus=1:mem=2gb -l walltime=1:59:00 -I
# def order_cols(cols, *order):
#     return list([c for c in order if c in cols]) + [c for c in cols if c not in order]
#
# c = ['datetime', 'duration', 'id', 'n', 'name', 'node', 'reps', 'size', 'time', 'timestamp', 'user', 'vnode']
# c = order_cols(c, 'id', 'nnn', 'size')
# print(c)
# exit(0)

script = '''
#!/bin/bash
#PBS -N bench-{tn}-{n}
#PBS -l select=1:ncpus=1:mem=1gb:cl_luna=True
#PBS -l walltime=01:59:59
#PBS -j oe

#
## P B S -m abe
## P B S -l scratch=1gb
if [ -n "$(type -t module)" ] && [ "$(type -t module)" = function ]; then
    echo "USING MODULES"
    module load python34-modules-gcc
    module list
    # module purge
    # module load /software/modules/current/metabase
    # # module load cmake-2.8.12
    # module load cmake-3.6.1
    # module load gcc-4.9.2
    # module load boost-1.56-gcc
    # module load perl-5.20.1-gcc
    # #module load mpich-3.0.2-gcc
    # module load openmpi
    # module load python-3.4.1-gcc
    # module load python34-modules-gcc
    #
    # module unload gcc-4.8.1
    # module unload openmpi-1.8.2-gcc
    # module unload python-2.7.6-gcc
    #
    # module list
else
    echo "not using modules"
fi

export LC_ALL=C

#mpstat -P ALL > {mpstat_filename} 2>&1 1 &
#MPSTAT_PID=$!
#sleep 2
for i in {{1..{reps}}}
do
    /usr/bin/time -f '{{"real": %e, "user": %U, "sys": %S}}' -o {time_filename} {command} -o {result_filename}
    #sleep 2
    #kill -INT $MPSTAT_PID
    #{debug_comment}{sys.executable} {collect_data_path} --mpstat "{mpstat_filename}" --time "{time_filename}" --result "{result_filename}"
    {sys.executable} {collect_data_path} --mpstat "{mpstat_filename}" --time "{time_filename}" --result "{result_filename}"
done

'''.strip()

db = None


def execute_no_pbs(t):
    global db
    if db is None:
        from db.mongo import Mongo
        db = Mongo()

    t.execute()
    db.bench5.insert_one(collect_data.decorate_result(t.json_result))
    return t


def execute_no_qsub(t):
    execute_benchmark(t, False)


def execute_qsub(t):
    execute_benchmark(t, True)


def execute_benchmark(t, use_qsub):
    import sys
    n = t.n
    tn = t.name
    reps = pargs.reps
    rnd = uuid.uuid4().hex
    command = ' '.join(t.command_line)
    filename = os.path.abspath('%s-%d-%s' % (t.family, t.n, rnd))
    shell_filename = filename + '.sh'
    time_filename = filename + '.time.json'
    mpstat_filename = filename + '.mpstat.txt'
    result_filename = filename + '.result.json'
    debug_comment = '' if use_qsub else '# '

    all = locals()
    all.update(globals())
    content = script.format(**all)

    with open(shell_filename, 'w') as fp:
        fp.write(content)
    os.chmod(shell_filename, 0o777)

    if use_qsub:
        process = subprocess.Popen(['qsub', shell_filename])
        process.wait()
    else:
        process = subprocess.Popen([shell_filename])
        print('%d=%d' % (process.pid, process.wait()))
        # collect_command = '-m {mpstat_filename} -t {time_filename} -r {result_filename}'.format(**locals()).split()
        # collect_data.main(collect_command)


if __name__ == '__main__':
    pargs = parse_args()
    mode = pargs.mode

    for i in range(pargs.reps if mode is Mode.LOCAL else 1):
        tests = TestGenerator.generate_tests(pargs)
        result = list()
        for r in range(1): # pargs.reps
            # print('Repetition %d of %d' % (r + 1, pargs.reps))

            for t in tests:
                if mode is Mode.LOCAL:
                    # result.append(
                    execute_no_pbs(t)
                    # )
                elif mode is Mode.SCRIPT:
                    result.append(
                        execute_no_qsub(t)
                    )
                elif mode is Mode.QSUB:
                    result.append(
                        execute_qsub(t)
                    )

    # if mode is Mode.LOCAL:
    #     from matplotlib import pyplot as plt
    #     from pluck import pluck
    #     import seaborn as sns
    #     import numpy as np
    #     import pandas as pd
    #
    #     durations = pluck(result, 'duration')
    #     n = pluck(result, 'n')
    #     rows = pluck(result, 'rows')
    #     df = pd.DataFrame()
    #     df['n'] = n
    #     df['dur'] = durations
    #     df['rows'] = rows
    #
    #     sns.regplot('rows', 'dur', df, order=2)
    #     plt.show()
    #
    #     plt.plot(rows, durations)
    #     plt.show()


# import collect_data
# collect_command = '-m aaa.mpstat.txt -t aaa.time.json -r aaa.result.json'.format(**locals()).split()
# collect_data.main(collect_command)
# exit(0)
#


    # with open(time_filename, 'r') as fp:
    #     time_info = json.load(fp)
    # os.unlink(time_filename)
    #
    # with open(mpstat_filename, 'r') as fp:
    #     mpstat_info = fp.read()
    #     lines = mpstat_info.splitlines()
    # os.unlink(mpstat_filename)
    #
    # headers = lines[2].split()
    # sections = list()
    # section = None
    # for line in lines[1:]:
    #     if not line.strip():
    #         if section:
    #             sections.append(section)
    #         section = list()
    #         continue
    #
    #     parts = [x.strip('\x00') for x in line.split()]
    #     cpu = parts[headers.index('CPU')]
    #     if cpu in ('CPU', 'all'):
    #         continue
    #
    #     result = dict(zip(headers[1:], parts[1:]))
    #     result = {k: float(v) if k.startswith('%') else v for k, v in result.items()}
    #     section.append(result)
    #
    # if section:
    #     sections.append(section)
    #
    # mpstat_json = dict()
    # mpstat_json['average'] = sections[-1]
    # mpstat_json['ticks'] = sections[0:-1]
    #
    # print(json.dumps(mpstat_json, indent=4))
