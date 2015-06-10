# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pointer's Gamut Visuals
=======================

Defines the *Pointer's Gamut*:

-   :def:`pointer_gamut_visual`
-   :def:`pointer_gamut_boundaries_visual`
-   :def:`pointer_gamut_hull_visual`
"""

from __future__ import division, unicode_literals

import numpy as np
from vispy.color.color_array import ColorArray
from vispy.scene.visuals import Line, Node

from colour import (
    Lab_to_XYZ,
    LCHab_to_Lab,
    POINTER_GAMUT_BOUNDARIES,
    POINTER_GAMUT_DATA,
    POINTER_GAMUT_ILLUMINANT,
    xy_to_XYZ)
from colour.plotting.volume import XYZ_to_reference_colourspace

from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT
from colour_analysis.visuals import Symbol

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['POINTER_GAMUT_DATA',
           'POINTER_GAMUT_BOUNDARIES',
           'pointer_gamut_visual',
           'pointer_gamut_boundaries_visual',
           'pointer_gamut_hull_visual']

POINTER_GAMUT_DATA = Lab_to_XYZ(LCHab_to_Lab(POINTER_GAMUT_DATA),
                                POINTER_GAMUT_ILLUMINANT)
"""
Pointer's Gamut data converted to *CIE XYZ* tristimulus values.

POINTER_GAMUT_DATA : ndarray
"""

POINTER_GAMUT_BOUNDARIES = xy_to_XYZ(POINTER_GAMUT_BOUNDARIES)
"""
Pointer's Gamut boundaries data converted to *CIE XYZ* tristimulus values.

POINTER_GAMUT_BOUNDARIES : ndarray
"""


def pointer_gamut_visual(reference_colourspace='CIE xyY',
                         size=4.0,
                         edge_size=0.5,
                         uniform_colour=(0.9, 0.9, 0.9),
                         uniform_opacity=0.8,
                         uniform_edge_colour=(0.9, 0.9, 0.9),
                         uniform_edge_opacity=0.8,
                         parent=None):
    """
    Returns a :class:`vispy.scene.visuals.Symbol` class instance representing
    Pointer's Gamut data using cross symbols.

    Parameters
    ----------
    reference_colourspace : unicode, optional
        {'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'IPT'}

        Reference colourspace to use for colour conversions / transformations.
    size : numeric, optional
        Cross size.
    edge_size : numeric, optional
        Cross edge size.
    uniform_colour : array_like, optional
        Uniform cross colour.
    uniform_opacity : numeric, optional
        Uniform cross opacity.
    uniform_edge_colour : array_like, optional
        Uniform cross edge colour.
    uniform_edge_opacity : numeric, optional
        Uniform cross edge opacity.
    parent : Node, optional
        Parent of the Pointer's Gamut visual in the `SceneGraph`.

    Returns
    -------
    Symbol
        Pointer's Gamut visual.
    """

    points = XYZ_to_reference_colourspace(POINTER_GAMUT_DATA,
                                          POINTER_GAMUT_ILLUMINANT,
                                          reference_colourspace)

    RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba
    RGB_e = ColorArray(uniform_edge_colour, alpha=uniform_edge_opacity).rgba

    markers = Symbol(symbol='cross',
                     positions=points,
                     size=size,
                     edge_size=edge_size,
                     face_colour=RGB,
                     edge_colour=RGB_e,
                     parent=parent)

    return markers


def pointer_gamut_boundaries_visual(reference_colourspace='CIE xyY',
                                    width=2.0,
                                    uniform_colour=(0.9, 0.9, 0.9),
                                    uniform_opacity=0.8,
                                    parent=None):
    """
    Returns a :class:`vispy.scene.visuals.Line` class instance representing
    Pointer's Gamut boundaries.

    Parameters
    ----------
    reference_colourspace : unicode, optional
        See :def:`pointer_gamut_visual` argument for possible values.

        Reference colourspace to use for colour conversions / transformations.
    width : numeric, optional
        Line width.
    uniform_colour : array_like, optional
        Uniform line colour.
    uniform_opacity : numeric, optional
        Uniform line opacity.
    parent : Node, optional
        Parent of the Pointer's Gamut boundaries visual in the `SceneGraph`.

    Returns
    -------
    Line
        Pointer's Gamut boundaries visual.
    """

    XYZ = np.vstack((POINTER_GAMUT_BOUNDARIES,
                     POINTER_GAMUT_BOUNDARIES[0, ...]))

    illuminant = DEFAULT_PLOTTING_ILLUMINANT

    points = XYZ_to_reference_colourspace(XYZ,
                                          illuminant,
                                          reference_colourspace)
    points[np.isnan(points)] = 0

    RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

    line = Line(points,
                RGB,
                width=width,
                method='agg',
                parent=parent)

    return line


def pointer_gamut_hull_visual(reference_colourspace='CIE xyY',
                              width=2.0,
                              uniform_colour=(0.9, 0.9, 0.9),
                              uniform_opacity=0.4,
                              parent=None):
    """
    Returns a :class:`vispy.scene.visuals.Node` class instance with
    :class:`vispy.scene.visuals.Lines` class instance children representing
    Pointer's Gamut hull.

    Parameters
    ----------
    reference_colourspace : unicode, optional
        See :def:`pointer_gamut_visual` argument for possible values.

        Reference colourspace to use for colour conversions / transformations.
    width : numeric, optional
        Lines width.
    uniform_colour : array_like, optional
        Uniform lines colour.
    uniform_opacity : numeric, optional
        Uniform lines opacity.
    parent : Node, optional
        Parent of the Pointer's Gamut hull visual in the `SceneGraph`.

    Returns
    -------
    Node
        Pointer's Gamut hull visual.
    """

    node = Node(parent=parent)

    pointer_gamut_data = np.reshape(POINTER_GAMUT_DATA, (16, -1, 3))
    for i in range(16):
        points = XYZ_to_reference_colourspace(
            np.vstack((pointer_gamut_data[i], pointer_gamut_data[i][0, ...])),
            POINTER_GAMUT_ILLUMINANT,
            reference_colourspace)

        points[np.isnan(points)] = 0

        RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

        Line(points, RGB, width=width, parent=node)
    return node
