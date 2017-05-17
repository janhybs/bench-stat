#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

from os.path import join, realpath, dirname
import uuid
import platform
import subprocess
import sys
import random

from git.csv import Repo
from pbs.actions import Seq, JobAction, MethodAction, ScriptAction

__dir__ = realpath(dirname(__file__))
__root__ = realpath(join(__dir__, '../'))
__bench__ = realpath(join(__root__, 'benchmarks'))

collect_script = realpath(join(__dir__, 'collect.py'))


qsub_template = """
#!/bin/bash
# #PBS -N install-flow
# #PBS -l select=1:ncpus=4:mem=4gb
# #PBS -l walltime=01:59:00
# #PBS -j oe
#
# # need to load following modules in order to build flow123d and its libs
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


WORKDIR=/tmp/bench-stat-{random_id}


mkdir -p $WORKDIR
cd $WORKDIR
{sys.executable} {collect_script} --test-id={t} --rep-id={r} --commit={latest}
rm  -rf $WORKDIR

""".strip()


# make_compile = ['make', 'compile']
# print(subprocess.check_call(make_compile, cwd=__bench__))


repo = Repo(__root__)
latest = repo.get_latest()


# tests = 19
# repetitions = 15
tests = 1
repetitions = 1
jobs = Seq('commit-'+latest[:7])
all = list()

for t in range(0, tests):
    for r in range(0, repetitions):
        random_id = uuid.uuid4().hex

        with Seq('experiment-t{t:02d}-r{r:02d}'.format(**locals())) as experiment:
            json_name = 'result.{}.{}.json'.format(platform.node(), random_id)
            result_json = realpath(join(__root__, 'results', json_name))

            binary = realpath(join(__bench__, 'O3.out'))

            # generate script
            script_name = 'qsub.{random_id}.sh'.format(**locals())
            script_content = qsub_template.format(**locals())
            qsub_file = realpath(join(__root__, 'results', script_name))
            open(qsub_file, 'w').write(script_content)

            job = ScriptAction('exec-t{t:02d}-r{r:02d}'.format(**locals()), qsub_file)
            collect_results = MethodAction('collect-results', lambda:None)

            experiment.add(job)     # this action will execute test
            all.append(experiment)

        # print(experiment)
        # run_test = [binary, result_json, '1.0.0', str(t)]
        # print(subprocess.check_call(run_test, cwd=__bench__))


random.shuffle(all)
jobs.add(*all)
print(jobs.browse())

jobs.start()


# hostname = platform.node().split('.')[0]
# nodename = hostname.strip('0123456789')
# print(result_json)