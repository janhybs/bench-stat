#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs


class JobStatus(object):
    QUEUED, RUNNING, EXITING, COMPLETED, UNKNOWN = 'QUEUED', 'RUNNING', 'EXITING', 'COMPLETED', '?'

    def __init__(self, status):
        self.status = status

    def __repr__(self):
        return '[{self.status}]'.format(self=self)

    @classmethod
    def parse(cls, value):
        return JobStatus(dict(
            Q=cls.QUEUED,
            R=cls.RUNNING,
            E=cls.EXITING,
            C=cls.COMPLETED,
            F=cls.COMPLETED,
        ).get(str(value).upper(), cls.UNKNOWN))


class Jobs(object):
    def __init__(self, jobs=list()):
        self.jobs = jobs

    def add(self, job):
        self.jobs.append(job)

    def wait(self, timeout=None):
        for job in self.jobs:
            for t in job.wait():
                print('%1.2f' % t, job)
                pass

    def __repr__(self):
        result = list()
        for job in self.jobs:
            result.append(str(job))
        return '\n'.join(result)


def configure(script, **kwargs):
    import os
    script = os.path.abspath(script)
    new_name = os.path.join(os.path.dirname(script), 'configured.' + os.path.basename(script))
    content = open(script, 'r').read()
    for key, value in kwargs.items():
        content = content.replace("@" + str(key) + "@", value)
    
    open(new_name, 'w').write(content)
    return new_name
    