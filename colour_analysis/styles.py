# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np


class Styles(object):
    def __init__(self, styles):
        self.__styles = styles
        self.__indexes = np.arange(len(styles))

    def current_style(self):
        return self.__styles[self.__indexes[0]]

    def next_style(self):
        self.__indexes = np.roll(self.__indexes, -1)

        return self.current_style()
