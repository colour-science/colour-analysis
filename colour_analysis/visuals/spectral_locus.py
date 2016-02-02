# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Spectral Locus Visual
=====================

Defines the *Spectral Locus Visual*:

-   :def:`spectral_locus_visual`
"""

from __future__ import division, unicode_literals

import numpy as np
from vispy.color.color_array import ColorArray
from vispy.scene.visuals import Line

from colour import XYZ_to_sRGB, normalise_maximum
from colour.plotting import get_cmfs
from colour.plotting.volume import XYZ_to_reference_colourspace

from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2016 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['spectral_locus_visual']


def spectral_locus_visual(reference_colourspace='CIE xyY',
                          cmfs='CIE 1931 2 Degree Standard Observer',
                          width=2.0,
                          uniform_colour=None,
                          uniform_opacity=1.0,
                          method='gl',
                          parent=None):
    """
    Returns a :class:`vispy.scene.visuals.Line` class instance representing
    the spectral locus.

    Parameters
    ----------
    reference_colourspace : unicode, optional
        {'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'IPT'}

        Reference colourspace to use for colour conversions / transformations.
    cmfs : unicode, optional
        Standard observer colour matching functions used to draw the spectral
        locus.
    width : numeric, optional
        Line width.
    edge_size : numeric, optional
        Symbol edge size.
    uniform_colour : array_like, optional
        Uniform symbol colour.
    uniform_opacity : numeric, optional
        Uniform symbol opacity.
    method : unicode, optional
        {'gl', 'agg'}

        Line drawing method.
    parent : Node, optional
        Parent of the spectral locus visual in the `SceneGraph`.

    Returns
    -------
    Line
        Spectral locus visual.
    """

    cmfs = get_cmfs(cmfs)
    XYZ = cmfs.values

    XYZ = np.vstack((XYZ, XYZ[0, ...]))

    illuminant = DEFAULT_PLOTTING_ILLUMINANT

    points = XYZ_to_reference_colourspace(XYZ,
                                          illuminant,
                                          reference_colourspace)
    points[np.isnan(points)] = 0

    if uniform_colour is None:
        RGB = normalise_maximum(XYZ_to_sRGB(XYZ, illuminant), axis=-1)
        RGB = np.hstack((RGB, np.full((RGB.shape[0], 1, np.float_),
                                      uniform_opacity)))
    else:
        RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

    line = Line(points,
                np.clip(RGB, 0, 1),
                width=width,
                method=method,
                parent=parent)

    return line
