#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs

import json
import base64


def base642obj(o):
    result = json.loads(base64.b64decode(o.encode()).decode())
    return result


def obj2base64(o):
    repr = json.dumps(o).encode()
    result = base64.b64encode(repr).decode()
    return result