#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import argparse
import sys
import os
import json
import getpass
import platform
import time
from utils import strings

from db.mongo import Mongo


def FileType(unlink=True, parse=None):
    def file_type(file_path):
        try:
            with open(file_path, 'r') as fp:
                content = fp.read()
            if unlink:
                os.unlink(file_path)
            return parse(content) if parse else content
        except Exception as e:
            return ''
    return file_type


def mpstat_parser(content):
    """
    :type content: str
    """

    lines = content.splitlines()
    info_line = lines[0]
    if len(lines) < 2:
        return dict(
            info=info_line,
            avg=[],
            ticks=[],
        )

    headers = lines[2].split()
    cpu_index = headers.index('CPU')

    sections = list()
    section = None
    for line in lines[1:]:
        if not line.strip():
            if section:
                sections.append(section)
            section = dict()
            continue

        parts = [x.strip('\x00') for x in line.split()]
        cpu = parts[cpu_index]
        if cpu in ('CPU', 'all'):
            continue

        result = dict(zip(headers[1:], parts[1:]))
        result = {k.strip('%').lower(): float(v) if k.startswith('%') else v for k, v in result.items()}
        section['c%s' % result['cpu']] = result

    if section:
        sections.append(section)
    average = sections[-1]
    cpus = list(average.keys())
    fields = list(list(average.values())[0].keys())

    # ticks = dict()
    # for c in cpus:
    #     ticks[c] = dict()
    #     for f in fields:
    #         ticks[c][f] = [t[c][f] for t in sections[0:-1]]

    ticks = {c: {f: [tick[c][f] for tick in sections[0:-1]] for f in fields} for c in cpus}

    mpstat = dict(info=info_line)
    mpstat['average'] = average
    mpstat['ticks'] = ticks
    return mpstat


def decorate_result(document):
    document['user'] = getpass.getuser()
    document['node'] = platform.node().split('.')[0].rstrip('1234567890')
    document['vnode'] = platform.node().split('.')[0]
    document['timestamp'] = time.time()

    if 'name' in document:
        name, prefix = str(document['name']), 'bench-'
        name = name[len(prefix):] if name.startswith(prefix) else name

        document['vname'] = name
        document['name'] = name.split('-')[0]
    return document


def main(command=None):

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mpstat', type=FileType(parse=mpstat_parser), help="location of mpstat output")
    parser.add_argument('-t', '--time', type=FileType(parse=json.loads), help="location of time command output")
    parser.add_argument('-r', '--result', type=FileType(parse=json.loads), help="json result file")
    parser.add_argument('--rest', type=strings.base642obj, help="Additional args in json structure")

    args, rest = parser.parse_known_args(command)
    # print(json.dumps(args.mpstat, indent=True))

    # from matplotlib import pyplot as plt
    #
    #
    # print(args.mpstat['ticks']['c0']['usr'], args.mpstat['ticks']['c1']['usr'])
    # plt.plot(args.mpstat['ticks']['c0']['usr'])
    # plt.plot(args.mpstat['ticks']['c1']['usr'])
    # plt.show()

    user_t, sys_t, real_t = args.time['user'], args.time['sys'], args.time['real']

    document = args.result.copy()
    if args.rest:
        document.update(args.rest)
    document['time'] = args.time
    document['time']['int1'] = (user_t + sys_t) / real_t
    document['time']['int2'] = user_t / real_t
    if args.mpstat:
        document['mpstat'] = args.mpstat
    decorate_result(document)

    from utils import textplot

    print('-' * 60)
    print('user:       {:5.2f}'.format(user_t))
    print('real:       {:5.2f}'.format(real_t))
    print('sys:        {:5.2f}'.format(sys_t))
    print('efficiency: {:5.2f}%'.format((user_t + sys_t) / real_t * 100))

    if args.mpstat:
        print('-'*60)
        plots = list()
        for p in args.mpstat['ticks']:
            print(args.mpstat['ticks'][p]['usr'])
            plots.append(args.mpstat['ticks'][p]['usr'])
        print('-' * 60)
        textplot.plot2(*plots)

    print(json.dumps(document, indent=4))

    db = Mongo()
    print(db.bench5.insert_one(document).inserted_id)


if __name__ == '__main__':
    main()

"""

0
user:       12.16
real:       13.25
sys:         0.21
efficiency: 93.36%

1
user:       12.32
real:       14.46
sys:         0.25
efficiency: 86.93%

16
user:       13.75
real:       16.03
sys:         0.20
efficiency: 87.02%

64
user:       13.81
real:       16.12
sys:         0.21
efficiency: 86.97%

256
user:       12.90
real:       14.80
sys:         0.14
efficiency: 88.11%

1024
user:       12.41
real:       14.81
sys:         0.15
efficiency: 84.81%


"""
