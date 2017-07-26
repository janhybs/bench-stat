#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs


import seaborn as sns; sns.set(color_codes=True)
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


data = pd.DataFrame([
    [1, 12.16, 13.25],
    [1*4, 12.32, 14.46],
    [16*4, 13.75, 16.03],
    [64*4, 13.81, 16.12],
    [256*4, 12.90, 14.80],
    [1024*4, 12.41, 14.81],
], columns=['mem-range', 'user', 'real'])
data['eff'] = data['user'] / data['real']
print(data)



sns.regplot('real', 'eff', data, logx=True)
# plt.plot(data['eff'])
plt.show()

