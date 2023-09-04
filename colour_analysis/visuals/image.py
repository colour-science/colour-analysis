# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image Visual
============

Defines the *Image Visual*:

-   :func:`image_visual`
"""

import numpy as np
# from vispy.scene.visuals import Image

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

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
