#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs


from os.path import join, realpath, dirname
import re
import datetime

__dir__ = realpath(dirname(__file__))
__root__ = realpath(join(__dir__, '../'))
__bench__ = realpath(join(__root__, 'benchmarks'))


main_hh_template = realpath(join(__bench__, 'main.template.hh'))
main_hh = realpath(join(__bench__, 'main.hh'))
version_txt = realpath(join(__root__, 'version'))
versions = realpath(join(__root__, 'versions.yaml'))


# default empty values
base = dict(
    MVS_S2__PER_LINE='',
    MVS_S2__BANDWIDTH='',
    MVS_S2__REPETITIONS='',

    MVS_S3__PER_LINE='',
    MVS_S3__BANDWIDTH='',
    MVS_S3__REPETITIONS='',

    MMS_S2__PER_LINE='',
    MMS_S2__BANDWIDTH='',
    MMS_S2__REPETITIONS='',

    MMS_S3__PER_LINE='',
    MMS_S3__BANDWIDTH='',
    MMS_S3__REPETITIONS='',
)


def configure(template, variables=None):
    """
    :type template: str
    """
    sub = '{:10s} //'
    replacements = base.copy()
    if variables:
        replacements.update(variables)

    # substitute all template variables add // at the end to suppress default value if value is valid
    for key, value in replacements.items():
        if value:
            template = re.sub(r'/\*\s*'+key+'\s*\*/', sub.format(str(value)), template)
        else:
            template = re.sub(r'/\*\s*' + key + '\s*\*/', '', template)
    return template


def new_version(variables=None, version='1.0.0'):
    src = open(main_hh_template, 'r').read()
    open(main_hh, 'w').write(configure(src, variables))
    open(version_txt, 'w').write(version + '\n')
