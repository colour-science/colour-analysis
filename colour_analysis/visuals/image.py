# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from vispy.scene.visuals import Image


def image_visual(image,
                 parent=None):
    image = np.clip(image, 0, 1)

    return Image(image, parent=parent)
