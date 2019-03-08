# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image Visual
============

Defines the *Image Visual*:

-   :func:`image_visual`
"""

from __future__ import division, unicode_literals

import numpy as np
from vispy.scene.visuals import Image

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2019 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['image_visual']


def image_visual(image, parent=None):
    """
    Returns a :class:`vispy.scene.visuals.Image` class instance using given
    image.

    Parameters
    ----------
    image : array_like
        Image.
    parent : Node, optional
        Parent of the image visual in the `SceneGraph`.

    Returns
    -------
    Image
        Image visual.
    """

    image = np.clip(image, 0, 1)

    return Image(image, parent=parent)
