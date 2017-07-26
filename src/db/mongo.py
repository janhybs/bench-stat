#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

from pymongo import MongoClient


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
        self.bench3 = self.db.get_collection('bench3')      # increasing size of a test

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
