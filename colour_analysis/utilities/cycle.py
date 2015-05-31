# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np


class Cycle(object):
    def __init__(self, items):
        self.__items = items
        self.__indexes = np.arange(len(items))

    def current_item(self):
        return self.__items[self.__indexes[0]]

    def next_item(self):
        self.__indexes = np.roll(self.__indexes, -1)

        return self.current_item()
