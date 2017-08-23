#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

import subprocess


class ExecutionResult(object):
    """
    Class ExecutionResult
     :type stdout      : str
     :type stderr      : str
     :type command     : list[str]
     :type error       : Exception
     :type returncode  : int
     :type broken      : bool
    """

    def __init__(self, stdout=None, stderr=None, error=None, command=None, returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.error = error
        self.command = command
        self.returncode = returncode
        self.broken = self.error is not None

    def __repr__(self):
        if self.broken:
            return 'ExecutionResult <{}>'.format(self.error)
        return 'ExecutionResult <[{}]: "{}"\n{}{}>'.format(
            self.returncode,
            ' '.join(self.command) if self.command else '',
            self.stdout, self.stderr
        )


def construct(command, *args):
    if isinstance(command, str):
        cmd = command.split()
    else:
        cmd = command

    cmd.extend(args)
    return cmd


def execute(cmd, cwd='.', timeout=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs):
    # try:
    #     process = subprocess.Popen(cmd, cwd=cwd, stdout=stdout, stderr=stderr, **kwargs)
    # except Exception as e:
    #     return ExecutionResult(error=e, command=cmd)
    #
    # returncode = None
    # stdout, stderr = list(), list()
    # while returncode is None:
    #     returncode = process.poll()
    #
    #     line = process.stdout.readline()
    #     stdout.append(line) if line is not None else None
    #
    #     line = process.stderr.readline()
    #     stderr.append(line) if line is not None else None
    #
    # return ExecutionResult('\n'.join(stdout), '\n'.join(stderr), command=cmd, returncode=returncode)

    try:
        process = subprocess.Popen(cmd, cwd=cwd, stdout=stdout, stderr=stderr, **kwargs)
        stdout, stderr = process.communicate(timeout=timeout)
        process.wait()
        return ExecutionResult(stdout.decode(), stderr.decode(), command=cmd, returncode=process.returncode)
    except Exception as e:
        print(e)
        return ExecutionResult(error=e, command=cmd)