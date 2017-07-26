#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import threading
import subprocess
import math

from pbs.pbspro import PBS


def _indent_generator(prefix, indent, suffix):
    def make_indent(level):
        if level == 0:
            return ''
        else:
            return prefix + indent * level + suffix
    return make_indent


class Action(threading.Thread):
    """
    Class Action
     :type actions : list[Action]
    """
    _formatter = _indent_generator('', '  ', '- ')

    def __init__(self, name):
        super(Action, self).__init__(name=name)
        self.action_name = name
        self.actions = list()

    def browse(self, level=0):
        result = list()
        result.append(self.__class__._formatter(level) + self.action_name)
        for action in self.actions:
            result.extend(action.browse(level + 1))

        if level == 0:
            return '\n'.join(result)
        return result

    def start(self):
        print('-' * 60 + self.action_name)
        super(Action, self).start()

    def add(self, *actions):
        self.actions.extend(actions)

    def __repr__(self):
        return '{self.__class__.__name__}.{self.action_name}({self.actions})'.format(self=self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def __len__(self):
        return len(self.actions)


class Seq(Action):
    def __init__(self, name):
        super(Seq, self).__init__(name)

    def run(self):
        for action in self.actions:
            action.start()
            action.join()


class Par(Action):
    _formatter = _indent_generator('', '  ', '= ')

    def __init__(self, name, limit=None):
        super(Par, self).__init__(name)
        self.limit = limit

    def start(self):
        if self.limit is None:
            for action in self.actions:
                action.start()

            for action in self.actions:
                action.join()
        else:
            total, l = len(self.actions), self.limit
            chunks = [self.actions[x * l:(x + 1) * l] for x in range(0, math.ceil(total / l))]

            for chunk in chunks:
                for action in chunk:
                    action.start()

                for action in chunk:
                    action.join()

        super(Par, self).start()


class RepoAction(Action):
    def __init__(self, name, repo, action, *args, **kwargs):
        super(RepoAction, self).__init__(name)

        self.repo = repo
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def run(self):
        getattr(self.repo, self.action)(*self.args, **self.kwargs)

    def __repr__(self):
        return '{self.__class__.__name__}.{self.action_name}({self.repo} {self.action} {self.args}, {self.kwargs})'.format(self=self)


class BashAction(Action):
    def __init__(self, name, commands):
        super(BashAction, self).__init__(name)
        self.args = commands
        self.returncode = None
        self.verbose = True

    def run(self):
        if type(self.args[0]) is not list:
            if self.verbose:
                print('$> {}'.format(' '.join([str(x) for x in self.args])))

            process = subprocess.Popen(self.args)
            self.returncode = process.wait()
        else:
            self.returncode = -256
            for arg in self.args:
                if self.verbose:
                    print('$> {}'.format(' '.join([str(x) for x in arg])))

                process = subprocess.Popen(arg)
                self.returncode = max(self.returncode, process.wait())


class ScriptAction(Action):
    def __init__(self, name, script, remove=False):
        super(ScriptAction, self).__init__(name)
        self.script = script
        self.returncode = None
        self.remove = remove

    def run(self):
        process = subprocess.Popen(['bash', self.script])
        self.returncode = process.wait()
        if self.remove:
            import os
            os.unlink(self.script)

    def __repr__(self):
        return '{self.__class__.__name__}.{self.action_name}({self.script})'.format(self=self)


class JobAction(Action):
    def __init__(self, name, script, pbs=PBS):
        super(JobAction, self).__init__(name)
        self.pbs = pbs
        self.script = script
        self.job = None
        self.returncode = None

    def run(self):
        self.job = self.pbs.qsub(self.script)
        for duration in self.job.wait():
            print('%1.2fs' % duration, self.job)
        self.returncode = 0

    def __repr__(self):
        return '{self.__class__.__name__}.{self.action_name}({self.script})'.format(self=self)


class MethodAction(Action):
    def __init__(self, name, method, *args, **kwargs):
        super(MethodAction, self).__init__(name)
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.method(*self.args, **self.kwargs)

    def __repr__(self):
        return '{self.__class__.__name__} {self.method.__name__}({self.args}, {self.kwargs})'.format(
            self=self)