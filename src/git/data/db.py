#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs
from pluck import pluck


class FlowDB(object):
    """
    Class FlowDB
     :type monitors     : list[pygit.csv.Branch]
    """

    aggregate_nodename = lambda commit: [
        {
            "$match": {
                "base.commit.hash": commit,
                "indices.parent": ""
            }
        },
        {
            '$group': {
                '_id': {
                    'nodename': '$base.nodename',
                    'task_size': '$base.task-size',
                    'cpu': '$base.run-process-count',
                    'test_name': '$base.test-name',
                    'case_name': '$base.case-name',
                },
                'count': {'$sum': 1}
            }
        }
    ]

    def __init__(self, mongo):
        """
        :type mongo: flowdb.mongo.Mongo
        """
        self.mongo = mongo
        self.monitors = []

    def add_branch_monitor(self, *branches):
        self.monitors.extend(branches)

    def commit_count(self, commit):
        commits = list(self.mongo.flow_long_log.find({'commit': commit.commit}))
        # print(commits)
        agg = self.__class__.aggregate_nodename(commit.commit)
        result = list(self.mongo.flow_long.aggregate(agg))
        import json
        print(json.dumps(result, indent=4))
        # if result:
        #     counts = dict(zip(pluck(result, '_id'), pluck(result, 'count')))
        #     print(counts)
            # return sum(counts.values())
        return len(commits)

    def check_commits_in_db(self):
        result = dict()
        for commit in set(self.monitors):
            result[commit] = self.commit_count(commit.commit)
        return result
        # exit(0)
        # # result = .limit(1)
        # # o = list(result)[0]
        # # print(result.count(True))
        # print(o['base']['commit']['hash'])

    def insert_commit(self, branch, ids):
        """
        :type ids: list[int]
        :type branch: pygit.csv.Branch or pygit.csv.Commit
        """

        data_to_insert = list()
        for id in ids:
            data_to_insert.append(dict(
                commit=branch.commit,
                seq_id=id,
            ))
        return self.mongo.flow_long_log.insert_many(data_to_insert)

    def _check_commits_in_db(self, branch):
        pass

    def __repr__(self):
        msg = ['Monitoring: ']
        for branch in self.monitors:
            msg.append(' - {branch.name:20s} latest commit: {branch.short_commit}'.format(**locals()))
        return '\n'.join(msg)
