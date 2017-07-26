#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs
from db.mongo import Mongo
import pandas as pd
import numpy as np
import seaborn as sns; sns.set(color_codes=True)
from matplotlib import pyplot as plt
from scipy.stats.stats import pearsonr

db = Mongo()
match = {
    '$match': {
        'node': 'janhybs'
    }
}
cursor = db.bench.aggregate([match,
    {
        '$group': {
            '_id': {
                'node': '$node',
                'name': '$name'
            },
            'dur': {'$push': '$duration'},
            'eff': {'$push': '$time.eff'},
            'real': {'$push': '$time.real'},
            'user': {'$push': '$time.user'},
            'sys': {'$push': '$time.sys'},
            'mp': {'$push': '$mpstat'},
            'size': {'$sum': 1}
        },
    },
    {
        '$sort': {'size': -1}
    }
])

groups = list(cursor)
for item in groups:
    item['name'] = item['_id']['name']
    item['node'] = item['_id']['node']

print(len(groups))
data = pd.DataFrame(groups)

del data['_id'], data['size']


plt.subplot(2, 2, 1)
for i in 1,2,3,4:
    plt.subplot(2, 2, i)
    subdata = data[data['name'] == 'bench-ma-%d' %i]
    if subdata.empty:
        continue

    props = 'eff', 'dur'
    d = pd.DataFrame(columns=subdata.columns)
    for p in 'real', 'user', 'sys', 'dur':
        d[p] = np.array(subdata[p].values[0])
    d['eff'] = d['user'] / d['real']

    coef = pearsonr(d[props[0]], d[props[1]])[0]
    sns.regplot(*props[:2], data=d)
    plt.title('%s vs %s = %1.3f' % (props[0], props[1], coef))
plt.show()


plt.subplot(2, 2, 1)
for i in 1,2,3,4:
    plt.subplot(2, 2, i)
    subdata = data[data['name'] == 'bench-ma-%d' %i]
    if subdata.empty:
        continue

    props = 'user',
    d = pd.DataFrame(columns=props)
    d[props[0]] = np.array(subdata[props[0]].values[0])

    sns.distplot(d[props[0]], bins=15)
    plt.title(props[0])
plt.show()

# data['eff2'] = data['user'] / data['real']
# g = groups[0]
# # for group in groups:
# #     if group['_id']['node'] == 'alfrid' and group['_id']['name'] == 'bench-ma-3':
# #         g = group
# #         break
#
# # g = groups[8]
#
# mp = list()
# for item in g['mp']:
#     t = list()
#     for i in range(0, 32):
#         if 'c%d' % i in item['average']:
#             t.append(item['average']['c%d' % i]['usr'])
#     mp.append(np.sum(t))
# g['mp'] = mp
# del g['_id'], g['size']
#

#
#
# props = 'mp', 'real'
# print(pearsonr(data[props[0]], data[props[1]])[0])
# sns.regplot(data=data, x=props[0], y=props[1])
# # plt.scatter(data['eff'], data['dur'])
# plt.show()