# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Spectral Locus Visual
=====================

Defines the *Spectral Locus Visual* and related visuals:

-   :def:`spectral_locus_visual`
-   :def:`chromaticity_diagram_construction_visual`
"""

from __future__ import division, unicode_literals

import numpy as np
from vispy.color.color_array import ColorArray
from vispy.scene.visuals import Line, Node

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

__all__ = ['spectral_locus_visual',
           'chromaticity_diagram_construction_visual']


def spectral_locus_visual(
    reference_colourspace='CIE xyY',
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
        RGB = np.hstack(
            (RGB, np.full((RGB.shape[0], 1), uniform_opacity, np.float_)))
    else:
        RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

    line = Line(points,
                np.clip(RGB, 0, 1),
                width=width,
                method=method,
                parent=parent)

    return line


def chromaticity_diagram_construction_visual(
    cmfs='CIE 1931 2 Degree Standard Observer',
    width=2.0,
    method='gl',
    parent=None):
    """
    Returns a :class:`vispy.scene.visuals.Line` class instance representing
    the chromaticity diagram construction with the spectral locus.

    Parameters
    ----------
    cmfs : unicode, optional
        Standard observer colour matching functions used to draw the spectral
        locus.
    width : numeric, optional
        Line width.
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

    from colour_analysis.visuals import Primitive

    node = Node(parent=parent)

    simplex_p = np.array([(1, 0, 0), (0, 1, 0), (0, 0, 1)])
    simplex_f = np.array([(0, 1, 2)])
    simplex_c = np.array([(1, 1, 1), (1, 1, 1), (1, 1, 1)])

    simplex = Primitive(simplex_p,
                        simplex_f,
                        uniform_opacity=0.5,
                        vertex_colours=simplex_c,
                        parent=node)

    simplex_f = np.array([(0, 1, 2), (1, 2, 0), (2, 0, 1)])
    simplex_w = Primitive(simplex_p,
                          simplex_f,
                          uniform_opacity=1.0,
                          vertex_colours=simplex_c,
                          wireframe=True,
                          parent=node)

    lines = []
    for XYZ in get_cmfs(cmfs).values:
        lines.append(XYZ * 1.75)
        lines.append((0, 0, 0))
    lines = np.array(lines)

    line = Line(lines,
                (0, 0, 0),
                width=width,
                method=method,
                parent=node)

    return node
