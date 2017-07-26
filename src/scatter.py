#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

from os.path import join, realpath, dirname
import uuid
import platform
import subprocess
import sys
import random
import math

from pluck import pluck

from db.flowdb import FlowDB
from db.mongo import Mongo
from git.csv import Repo
from pbs.actions import Seq, JobAction, MethodAction, ScriptAction, Par


__dir__ = realpath(dirname(__file__))
__root__ = realpath(join(__dir__, '../'))
__bench__ = realpath(join(__root__, 'benchmarks'))

collect_script = realpath(join(__dir__, 'collect.py'))


qsub_template = """
#!/bin/bash
# #PBS -n install-flow
# #PBS -l select=1:ncpus=4:mem=4gb{restriction_command}
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

export RESTRICTIONS={restriction_command}
WORKDIR=/tmp/bench-stat-{random_id}


mkdir -p $WORKDIR
cd $WORKDIR
{sys.executable} {collect_script} --test-id={test_id} --rep-id={rep_id} --commit={latest}
rm  -rf $WORKDIR

""".strip()

# repo = Repo(__root__)
# latest = repo.get_latest()
flowdb = FlowDB(Mongo())
latest = 'c4a410af274b9e6a6a5075214b2b5d38498e27ab'


# tests = 19
# repetitions = 15
tests = 1
repetitions = 50


indices = [(test_id, rep_id) for test_id in range(0, tests) for rep_id in range(0, repetitions)]
random.shuffle(indices)


def get_restrictions(commit, test):
    restrictions = list()
    the_most_frequent = flowdb.get_test_stat(latest, test_id)[:3]
    for frequent in the_most_frequent:
        if frequent['count'] > 2:
            restrictions.append(':cl_{f[_id]}=False'.format(f=frequent))
    return ''.join(restrictions)

limit = 5
chunk = 0
experiments = Par('commit-{}-{}'.format(latest[:7], chunk))

for test_id, rep_id in indices:
    with Seq('experiment-t{test_id:02d}-r{rep_id:02d}'.format(**locals())) as experiment:

        # look in db and exclude 3 most frequently used nodes
        # exclude only if number of experiments for test is greater then 2
        restriction_command = get_restrictions(latest, test_id)

        # generate script
        random_id = uuid.uuid4().hex
        script_name = 'qsub.{random_id}.sh'.format(**locals())
        script_content = qsub_template.format(**locals())
        qsub_file = realpath(join(__root__, 'results', script_name))
        open(qsub_file, 'w').write(script_content)

        # create jobs
        job = ScriptAction('exec-t{test_id:02d}-r{rep_id:02d}'.format(**locals()), qsub_file, remove=True)
        experiments.add(job)

        # execute another batch
        if len(experiments) == limit:
            experiments.start()
            experiments.join()

            chunk += 1
            experiments = Par('commit-{}-{}'.format(latest[:7], chunk))
            break

# execute rest
if len(experiments) > 0:
    experiments.start()
    experiments.join()


# import seaborn as sns
# from matplotlib import pyplot as plt
# data = flowdb.get_test_stat(latest, 0)
# sns.distplot(data, )
# plt.show()

# shuffle jobs
# print(jobs.browse())


# start them
# jobs.start()


# hostname = platform.node().split('.')[0]
# nodename = hostname.strip('0123456789')
# print(result_json)