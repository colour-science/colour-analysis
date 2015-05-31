# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.scene.visuals import Markers


class Symbol(Markers):
    def __init__(self,
                 symbol='disc',
                 points=None,
                 size=4.0,
                 edge_size=0.5,
                 face_color=None,
                 edge_color=None,
                 scaling=False,
                 parent=None):
        Markers.__init__(self)

        self.set_data(points,
                      size=size,
                      edge_width=edge_size,
                      face_color=face_color,
                      edge_color=edge_color,
                      scaling=scaling)
        self.set_symbol(symbol)

        if parent is not None:
            parent.add(self)
