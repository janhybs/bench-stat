#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs


import os
import datetime
from git.cmd.utils import construct, execute


class Branch(object):
    def __init__(self, commit, name, type='commit', relative_date='', actual_date=None):
        self.commit = commit
        self.short_commit = commit[:7]
        self.name = name
        self.short_name = name.split('/')[-1]
        self.type = type
        self.remote = self.name.startswith('origin/')
        self.relative_date = relative_date
        if actual_date:
            self.actual_date = datetime.datetime.strptime(actual_date, '%Y-%m-%d')

    def __repr__(self):
        return '{self.short_commit}-{self.name}'.format(self=self)

    def __eq__(self, other):
        return self.commit == other.commit

    def __hash__(self):
        return hash(self.commit)


class Commit(object):
    def __init__(self, commit, user, email, relative_date, message):
        self.commit = commit
        self.short_commit = commit[:7]
        self.user = user
        self.email = email
        self.relative_date = relative_date
        self.message = message

    def __eq__(self, other):
        return self.commit == other.commit

    def __hash__(self):
        return hash(self.commit)

    def __repr__(self):
        return '{self.short_commit}-{self.user} ({self.relative_date})'.format(self=self)


class Repo(object):
    """
    Class Repo
    :type branches             : list[Branch]
    """

    def __init__(self, location, auto_fetch=True, clone=False):
        self.branches = []
        self.cwd = location
        self.name = os.path.basename(self.cwd)
        self.verbose = True

        if not os.path.exists(location):
            if not clone:
                raise FileNotFoundError("Given location does not exists: %s" % str(location))

            self.execute('git clone', clone, self.cwd, cwd='/')

        if auto_fetch:
            print(self._fetch().stdout)
        self._load_branches()
        # print('Local branches:')
        # print('    ' + '\n    '.join([str(x) for x in self.get_branches(type='commit', remote=False)]))

    def execute(self, cmd, *args, **kwargs):
        command = construct(cmd, *args)
        if self.verbose:
            print('$> {}'.format(' '.join([str(x) for x in command])))
        return execute(construct(cmd, *args), cwd=kwargs.pop('cwd', self.cwd), **kwargs)

    def get_branches(self, **kwargs):
        if not kwargs:
            return self.branches.copy()
        else:
            result = []
            for b in self.branches.copy():
                match = True
                for k, v in kwargs.items():
                    if getattr(b, k) != v:
                        match = False
                        break
                if match:
                    result.append(b)
            return result

    def _fetch(self):
        return self.execute('git fetch')

    def _load_branches(self):
        result = self.execute(
            'git for-each-ref',
            "--format=%(objectname)|%(refname:short)|%(objecttype)|%(committerdate:relative)|%(committerdate:short)"
        )
        if result.returncode == 0:
            self.branches = [Branch(*x.split('|')) for x in result.stdout.splitlines()]
        else:
            print(result.stderr)

    def checkout(self, commit):
        self.execute('git checkout -f', commit)

    def get_latest(self):
        return self.get_branches(name='origin/master')[0].commit

    def __repr__(self):
        return 'Repo({self.name})'.format(self=self)

    def info(self):
        lines = self.execute('git log -3', '--format=[%h] %an (%ae), %ar - %s').stdout.splitlines()
        result = []
        for line in lines:
            result.append('    ' + line)
            result.append('        |')
        return '\n'.join(result[:-1])

    def get_last_commit_for_branch(self, branch, count=10):
        command = 'git log {branch}~{count}..{branch} --oneline --reverse'
        lines = self.execute(command.format(**locals()), '--format=%H|%an|%ae|%ar|%s').stdout.splitlines()
        commits = [Commit(*line.split('|')) for line in lines]
        return commits