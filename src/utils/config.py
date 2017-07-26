#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import os
import yaml
import enum


class Config(object):
    _instance = None
    _cfg = dict()

    @classmethod
    def _load_config(cls):
        if cls._instance:
            return cls._instance

        current = 0
        max_limit = 10
        root = os.path.dirname(__file__)

        config_file = os.path.join(root, '.config.yaml')
        while current < max_limit:
            config_file = os.path.join(root, '.config.yaml')
            current += 1
            if os.path.exists(config_file):
                break
            root = os.path.dirname(root)
        # load config and extract username and password

        cls._instance = Config()
        cls._cfg = yaml.load(open(config_file, 'r').read()) or dict()
        return cls._instance

    def get(self, key=None, default=None):
        """
        :rtype: dict or list or string or int or bool
        """
        self.__class__._load_config()
        if key is None:
            return self.__class__._cfg

        keys = str(key).split('.')
        if len(keys) == 1:
            return self.__class__._cfg.get(key, default)

        r = self.__class__._cfg
        for k in keys:
            r = r[k]
        return r

    def set(self, key, value):
        """
        :rtype: dict or list or string or int or bool
        """
        self.__class__._load_config()
        self.__class__._cfg[key] = value
        return value

    def __getitem__(self, item):
        return self.get(item)

    def __repr__(self):
        cfg = self.__class__._cfg.copy()
        cfg['pymongo']['password'] = '---HIDDEN---'
        return yaml.dump(cfg, indent=4)

cfg = Config()


class Mode(enum.Enum):
    LOCAL = 'local'
    SCRIPT = 'script'
    QSUB = 'qsub'

    def __eq__(self, other):
        return self.value == other

    def __hash__(self):
        return hash(self.value)

    @classmethod
    def parse(cls, value):
        for o in cls:
            if o.value == value:
                return o
        raise IndexError('No such enum value %s' % value)

    @classmethod
    def values(cls):
        return [o.value for o in cls]