#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# author:linbirg

from www.common.vo import ViewObj


class VoPage(ViewObj):
    page = {'totalItem': 10, 'currentPage': 1, 'pageSize': 10}
