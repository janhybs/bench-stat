#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs


import seaborn as sns
import pandas as pd
import numpy as np
from db.mongo import Mongo
from matplotlib import pyplot as plt
from scipy.stats.stats import pearsonr

sns.set(color_codes=True)

db = Mongo()
match = {'$match': {
    'node': 'luna',
    # 'name': 'bench-ma-3'
}}
cursor = db.bench2.aggregate([match,
    {
        '$group': {
            '_id': {
                'family': '$family',
                'name': '$name'
            },
            'dur': {'$push': '$duration'},
            'eff': {'$push': '$time.eff'},
            'real': {'$push': '$time.real'},
            'user': {'$push': '$time.user'},
            'mp': {'$push': '$mpstat'},
            'size': {'$sum': 1}
        },
    },
    {
        '$sort': {'size': -1}
    }
])

items = list(cursor)
for item in items:
    item['abs'] = item['real'][1] - item['real'][0]
    item['rel'] = abs(item['abs'] / item['real'][1])
    item['a'] = item['real'][0]
    item['b'] = item['real'][1]
    item['size'] = int(item['_id']['name'].lstrip('bench-ma'))

data = pd.DataFrame(items)
del data['eff']
del data['mp']
# del data['size']
# del data['_id']

# sns.distplot(data['rel'])

plt.subplot(2, 2, 1)
for i in 1,2,3,4:
    subdata = data[data['size'] == i]
    props = 'a', 'b'

    plt.subplot(2, 2, i)
    sns.regplot(*props, data=subdata)
    coef = pearsonr(subdata[props[0]], subdata[props[1]])[0]
    plt.title('p=%1.3f' % coef)
plt.show()

plt.subplot(2, 1, 1)
sns.distplot(data[data['size'] == 1]['abs'])
sns.distplot(data[data['size'] == 2]['abs'])
sns.distplot(data[data['size'] == 3]['abs'])
sns.distplot(data[data['size'] == 4]['abs'])
plt.title('A - B')

plt.subplot(2, 1, 2)
sns.distplot(data[data['size'] == 1]['rel'], label='1')
sns.distplot(data[data['size'] == 2]['rel'], label='2')
sns.distplot(data[data['size'] == 3]['rel'], label='3')
sns.distplot(data[data['size'] == 4]['rel'], label='4')
plt.legend()
plt.title('(A - B)/B')

plt.show()