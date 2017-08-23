#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

from pymongo import MongoClient
import pandas as pd
import time


class Mongo(object):
    """
    Class Mongo manages connection and queries
    :type db          : pymongo.database.Database
    :type bench       : pymongo.database.Collection
    :type nodes       : pymongo.database.Collection
    :type flat        : pymongo.database.Collection
    :type fs          : pymongo.database.Collection
    """

    def __init__(self, auto_auth=True):
        self.client = MongoClient('hybsntb.nti.tul.cz')
        self.db = self.client.get_database('bench')
        # self.bench = self.db.get_collection('bench')
        # self.bench_new = self.db.get_collection('bench_new')
        # self.nodes = self.db.get_collection('nodes')
        # self.flat = self.db.get_collection('flat_copy')
        # self.fs = self.db.get_collection('fs')
        # self.flow_long = self.db.get_collection('flow_long')
        # self.flow_long_log = self.db.get_collection('flow_long_log')

        self.bench = self.db.get_collection('bench')        # testing mpstat and time to detect outliers
        self.bench2 = self.db.get_collection('bench2')      # running 2 tests along side to see if they are affected in the same way
        self.bench3 = self.db.get_collection('bench3')      # running 2 tests along side to see if they are affected in the same way
        self.bench4 = self.db.get_collection('bench4')      # time resolution
        self.bench5 = self.db.get_collection('bench5')      # time resolution

        if auto_auth and self.needs_auth():
            self.auth()

    def needs_auth(self):
        try:
            self.db.collection_names()
            return False
        except:
            return True
    
    def auth(self, username=None, password=None):
        if username is None:
            from utils.config import cfg
            username = cfg.get('pymongo').get('username')
            password = cfg.get('pymongo').get('password')

        return self.client.admin.authenticate(username, password)

    def __repr__(self):
        return 'DB({self.client.address[0]}:{self.client.address[1]})'.format(self=self)

    @classmethod
    def convert(cls, cursor, keep_id=False):
        items = list(cursor)
        i = 0
        for item in items:
            i += 1
            if 'timestamp' not in item:
                item['timestamp'] = cls.id2timestamp(item['_id'])
            item['datetime'] = item['_id'].generation_time
            item['name'] = item['name'].replace('bench-', '')
            item['id'] = i
        data = pd.DataFrame(items)
        if not keep_id:
            del data['_id']

        preferred_order = cls.order_cols(data.columns.tolist(), 'id', 'name', 'n', 'size', 'duration')
        return data[preferred_order]

    @classmethod
    def order_cols(cls, cols, *order):
        return list([c for c in order if c in cols]) + [c for c in cols if c not in order]

    @classmethod
    def id2timestamp(cls, value):
        return time.mktime(value.generation_time.timetuple())
