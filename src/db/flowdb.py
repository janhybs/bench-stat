#!/usr/bin/python
# -*- coding: utf-8 -*-
# author:   Jan Hybs

from pluck import pluck

count_aggregate = lambda commit, test_id: [
    {
        '$match': {
            'commit': commit,
            'test_id': test_id,
        }
    },
    {
        '$group': {
            '_id': '$nodename',
            'count': {'$sum': 1},
        }
    }
]


class FlowDB(object):
    def __init__(self, mongo):
        """
        :type mongo: db.mongo.Mongo
        """
        self.mongo = mongo

    def get_test_stat(self, commit, test_id):
        aggregate_query = count_aggregate(commit, test_id)
        result = list(self.mongo.bench_new.aggregate(aggregate_query))
        result.sort(key=lambda x: x['count'], reverse=True)
        return result
