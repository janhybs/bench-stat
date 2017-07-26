#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import sys
import math

size = None
space = ' '


def pp(r):
    for row in r:
        print(''.join([' ' if not r else r for r in row]))


def reshape(a, rows, cols):
    return [a[i*cols:(i+1)*cols] for i in range(rows)]


def write(s, r, y, x=0, center=0):
    s = str(s)

    if center:
        s = ('{:^%ds}' % center).format(s)

    l = len(s)
    if x + l > len(r[y]):
        x = len(r[y]) - l

    # r[y, x:x+l] = s
    for i in range(x,x+l):
        r[y, i] = s[i-x]


def plot(*y):
    import shutil
    import numpy as np
    cols, rows = shutil.get_terminal_size((80, 24))

    sample_size = len(y[0])

    X = np.arange(sample_size)

    lm = 10
    bm = 3

    xs = int((cols - lm)/lm)
    X_ticks = np.linspace(lm, cols, xs, dtype=np.int)
    X_labels = X

    ys = int((rows - bm)/bm)
    Y_ticks = np.linspace(0, rows-bm-1, ys, dtype=np.int)
    Y_labels = np.linspace(0, 100, ys, dtype=np.int)[::-1]

    result = np.chararray((rows, cols), unicode=True)
    result[:] = space

    result[:, :lm] = space
    result[:, lm] = '|'

    result[-bm:, :] = space
    result[-bm, lm:] = '-'

    result[-bm, lm] = '\\'

    for i in range(xs):
        write(X_labels[i], result, rows-1, X_ticks[i])

    for i in range(ys):
        write(Y_labels[i], result, Y_ticks[i], 0, 10)

    def plot_series(Y, symbol='*'):
        for i in range(lm+1, cols):
            index = (i - 1 - lm) / lm
            base = int(index)
            interp = (Y[base] - Y[base+1]) * (index - base)
            value = Y[base] - interp
            y_value = int(rows - bm - (value/100 * (rows - bm)))
            result[y_value, i] = symbol

    symbols = list('abcdefghijklmnopqrstuvwxyz,+=-:.*○●')
    for Y in y:
        plot_series(Y, symbols.pop())

    pp(result)


def plot2(*y):
    # ■◩◪◧◗
    samples = len(y[0])

    charts = list()
    for j in range(len(y)):
        chart = list()
        Y = y[j]
        chart.append('{:-^24s}'.format('CPU-%d' % j))
        for i in range(len(Y)):
            total = int((Y[i] / 100.0) * 20)
            blur = 1 if (Y[i] - total * 5) > 2.5 else 0

            line = '{i:2d}|{p:20s}|'.format(p='■' * total + '◧' * blur, i=i)

            chart.append(line)
        chart.append(' '*24)
        charts.append(chart)

    if len(charts) == 1:
        charts = [charts]

    elif len(charts) == 2:
        charts = reshape(charts, rows=1, cols=2)

    elif len(charts) <= 4:
        charts = reshape(charts, rows=2, cols=2)

    elif len(charts) <= 8:
        charts = reshape(charts, rows=2, cols=4)

    elif len(charts) <= 12:
        charts = reshape(charts, rows=4, cols=3)

    elif len(charts) <= 16:
        charts = reshape(charts, rows=4, cols=4)

    elif len(charts) <= 24:
        charts = reshape(charts, rows=4, cols=6)

    elif len(charts) <= 32:
        charts = reshape(charts, rows=4, cols=8)

    else:
        charts = reshape(charts, rows=math.ceil(len(charts)/8), cols=8)


    for chart in charts:
        for i in range(samples+2):
            line = ''
            if type(chart) is list:
                for subchart in chart:
                    line += subchart[i]
            else:
                line = chart[i]

            lineutf = (line + '\n').encode('utf-8')
            sys.stdout.buffer.write(lineutf)
            # print(line)
