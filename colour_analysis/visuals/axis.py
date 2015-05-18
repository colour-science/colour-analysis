# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from vispy.scene.visuals import create_visual_node
from vispy.visuals.line import LineVisual


class AxisVisual(LineVisual):
    def __init__(self, scale=1.0, **kwargs):
        vertices = np.array([[0, 0, 0],
                             [1, 0, 0],
                             [0, 0, 0],
                             [0, 1, 0],
                             [0, 0, 0],
                             [0, 0, 1]])
        vertices *= scale
        colour = np.array([[1, 0, 0, 1],
                           [1, 0, 0, 1],
                           [0, 1, 0, 1],
                           [0, 1, 0, 1],
                           [0, 0, 1, 1],
                           [0, 0, 1, 1]])

        LineVisual.__init__(self,
                            pos=vertices,
                            color=colour,
                            connect='segments',
                            method='gl',
                            **kwargs)


Axis = create_visual_node(AxisVisual)


def axis_visual(scale=1.0, parent=None):
    return Axis(scale=scale, parent=parent)
