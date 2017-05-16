#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import time
import subprocess
from pbs import JobStatus


class LocalPBS(object):
    @classmethod
    def qsub(cls, file=None):
        process = subprocess.Popen(['bash', file])
        return Job(process)

    @classmethod
    def qstat(cls, job):
        rc = job.process.poll()
        if rc is None:
            job.status = JobStatus(JobStatus.RUNNING)
        else:
            job.status = JobStatus(JobStatus.COMPLETED)
        return job


class Job(object):
    def __init__(self, process):
        super(Job, self).__init__()
        self.process = process
        self.status = JobStatus(JobStatus.UNKNOWN)
        self.qstat()

    def qstat(self):
        return LocalPBS.qstat(self)

    def is_finished(self):
        return self.status.status == JobStatus.COMPLETED

    def __repr__(self):
        return '{self.status} [{self.process}]'.format(self=self)

    def wait(self, timeout=None, interval=5):
        if timeout:
            print('[INFO] waiting on job:', self, 'maximum of %ds until job status changes to COMPLETED' % timeout)
        else:
            print('[INFO] waiting on job:', self, 'until job status changes to COMPLETED')

        start = time.time()
        while not self.is_finished():
            self.qstat()
            if timeout and self.status != JobStatus.COMPLETED and (time.time() - start) > timeout:
                print('[WARN] Breaking waiting loop - job did not finish, job is currently', self.status.status)
                break
            yield time.time() - start
            if self.is_finished():
                break
            time.sleep(interval)

