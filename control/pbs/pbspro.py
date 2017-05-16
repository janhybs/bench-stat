#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import subprocess
import re
import time

from pbs import JobStatus


class Job(object):
    fields = dict(
        job_state=('status', JobStatus.parse),
        queue=('queue', str),
        Job_Name=('job_name', str),
        server=('server', str),
    )

    def __init__(self, job_id):
        self.job_id = job_id
        self.job_name = '<no_name>'
        self.status = JobStatus(JobStatus.UNKNOWN)
        self.queue = '<no_queue>'
        self.server = '<unknown_server>'
        self.qstat()

    def wait(self, timeout=None, interval=5):
        if timeout:
            print('[INFO] waiting on job:', self, 'maximum of %ds until job status changes to COMPLETED' % timeout)
        else:
            print('[INFO] waiting on job:', self, 'until job status changes to COMPLETED')

        start = time.time()
        while self.status.status != JobStatus.COMPLETED:
            self.qstat()
            if timeout and self.status != JobStatus.COMPLETED and (time.time() - start) > timeout:
                print('[WARN] Breaking waiting loop - job did not finish, job is currently', self.status.status)
                break
            yield time.time() - start
            time.sleep(interval)

    def qstat(self):
        return PBS.qstat(self)

    def __repr__(self):
        return '{self.status} [{self.job_id}] {self.job_name} in queue {self.queue} ({self.server})'.format(self=self)


class PBS(object):
    id_regex = re.compile('(\d+)')

    @classmethod
    def qsub(cls, file=None):
        output = subprocess.check_output(['qsub', file]).decode().strip()
        # output = subprocess.check_output('echo 1172554.arien-pro.ics.muni.cz'.split()).decode().strip()
        job_id, = cls.id_regex.findall(output)
        return Job(job_id)

    @classmethod
    def qstat(cls, job):
        output = subprocess.check_output(['qstat', '-xf', job.job_id]).decode().strip()
    #     output = """Job Id: 1172551.arien-pro.ics.muni.cz
    # Job_Name = manegrot_2n_4p_ib
    # Job_Owner = jan-hybs@META
    # resources_used.cpupercent = 1970
    # resources_used.cput = 01:11:39
    # resources_used.mem = 3806392kb
    # resources_used.ncpus = 8
    # resources_used.vmem = 6531624kb
    # resources_used.walltime = 00:12:52
    # job_state = R
    # queue = q_2h
    # server = arien-pro.ics.muni.cz
    # Checkpoint = u
    # ctime = Thu Apr 13 12:45:45 2017
    # Error_Path = tarkil.grid.cesnet.cz:/auto/praha1/jan-hybs/projects/Flow123dD
    # ocker/cluster_comparison/bin/manegrot_2n_4p_ib.e1172551
    # exec_host = manegrot2/2*4+manegrot2/3*4
    # exec_host2 = manegrot2.ics.muni.cz:15002/2*4+manegrot2.ics.muni.cz:15002/3*
    # 4
    # exec_vnode = (manegrot2:ncpus=4:mem=8192000kb)+(manegrot2:ncpus=4:mem=81920
    # 00kb)
    # Hold_Types = n
    # Join_Path = n
    # Keep_Files = n
    # Mail_Points = a
    # mtime = Thu Apr 13 13:19:23 2017
    # Output_Path = tarkil.grid.cesnet.cz:/auto/praha1/jan-hybs/projects/Flow123d
    # Docker/cluster_comparison/bin/manegrot_2n_4p_ib.o1172551
    # Priority = 0
    # qtime = Thu Apr 13 12:45:45 2017
    # Rerunable = True
    # Resource_List.mem = 16000mb
    # Resource_List.mpiprocs = 8
    # Resource_List.ncpus = 8
    # Resource_List.nodect = 2
    # Resource_List.place = free
    # Resource_List.select = 2:ncpus=4:mem=8000mb:cl_manegrot=True:mpiprocs=4
    # Resource_List.walltime = 01:59:00
    # stime = Thu Apr 13 13:06:32 2017
    # session_id = 13160
    # jobdir = /storage/brno2/home/jan-hybs
    # substate = 42
    # Variable_List = PBS_O_SYSTEM=Linux,GROUP=meta,
    # PBS_O_HOME=/storage/praha1/home/jan-hybs,
    # PBS_O_HOST=tarkil.grid.cesnet.cz,TORQUE_RESC_MEM=16777216000,
    # PBS_RESC_TOTAL_MEM=16777216000,JOBID=1172551.arien-pro.ics.muni.cz,
    # PBS_O_LOGNAME=jan-hybs,TORQUE_RESC_PROC=8,PBS_O_LANG=en_US.UTF-8,
    # USER=jan-hybs,TORQUE_RESC_TOTAL_PROCS=8,PBS_O_MAIL=/var/mail/jan-hybs,
    # PBS_RESC_MEM=16777216000,PBS_NUM_PPN=8,PBS_RESC_TOTAL_PROCS=8,
    # PBS_O_SHELL=/bin/bash,HOSTNAME=manegrot2.ics.muni.cz,
    # PBS_O_QUEUE=default,
    # PBS_O_WORKDIR=/auto/praha1/jan-hybs/projects/Flow123dDocker/cluster_co
    # mparison/bin,
    # PBS_O_PATH=/software/python/2.7.10/gcc/bin:/software/python27-modules/
    # software/python-2.7.6/gcc/bin:/software/openmpi-1.6.5/gcc/bin:/software
    # /perl-5.20.1/gcc/bin:/software/python-2.7.6/gcc/bin:/software/gcc/4.9.2
    # /bin:/afs/ics.muni.cz/software/cmake-2.8/cmake-2.8.12/bin:/usr/local/bi
    # n:/usr/bin:/bin:/usr/local/games:/usr/games:/usr/bin:/software/meta-uti
    # ls/internal:/software/meta-utils/public,PBS_NCPUS=8,
    # TORQUE_RESC_TOTAL_WALLTIME=7140,PBS_RESC_TOTAL_WALLTIME=7140,
    # PBS_NUM_NODES=1,TORQUE_RESC_TOTAL_MEM=16777216000
    # comment = Job run at Thu Apr 13 at 13:06 on (manegrot2:ncpus=4:mem=8192000k
    # b)+(manegrot2:ncpus=4:mem=8192000kb)
    # etime = Thu Apr 13 12:45:45 2017
    # run_count = 1
    # Submit_arguments = generated_10s/manegrot_2n_4p_ib.sh
    # project = _pbs_project_default
    # krb_princ = jan-hybs@META
    # Job_Host = tarkil.grid.cesnet.cz
    #
    #     """
        lines = output.strip().splitlines()
        for start, config in Job.fields.items():
            name, func = config

            for line in lines:
                line = line.strip()
                if line.startswith(start):
                    value = line[len(start):].lstrip(' =')
                    setattr(job, name, func(value))

        return job
