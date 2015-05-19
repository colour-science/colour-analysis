# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.scene.visuals import XYZAxis
from vispy.visuals.transforms import AffineTransform


def axis_visual(scale=1.0, parent=None):
    axis = XYZAxis(parent=parent)

    transform = AffineTransform()
    transform.scale(scale)
    axis.transform = transform

    return axis
