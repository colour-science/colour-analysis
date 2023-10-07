# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pointer's Gamut Visuals
=======================

Defines the *Pointer's Gamut*:

-   :func:`pointer_gamut_visual`
-   :func:`pointer_gamut_boundaries_visual`
-   :func:`pointer_gamut_hull_visual`
"""

import numpy as np
# from vispy.color.color_array import ColorArray
# from vispy.scene.visuals import Line, Node

# from colour import (Lab_to_XYZ, LCHab_to_Lab, POINTER_GAMUT_BOUNDARIES,
#                     POINTER_GAMUT_DATA, POINTER_GAMUT_ILLUMINANT, xy_to_XYZ)
# from colour.models import XYZ_to_colourspace_model
from colour.plotting.volume import colourspace_model_axis_reorder

from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT
from colour_analysis.visuals import Symbol

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    'POINTER_GAMUT_DATA', 'POINTER_GAMUT_BOUNDARIES', 'pointer_gamut_visual',
    'pointer_gamut_boundaries_visual', 'pointer_gamut_hull_visual'
]

# POINTER_GAMUT_DATA = Lab_to_XYZ(
#     LCHab_to_Lab(POINTER_GAMUT_DATA), POINTER_GAMUT_ILLUMINANT)
# """
# Pointer's Gamut data converted to *CIE XYZ* tristimulus values.
#
# POINTER_GAMUT_DATA : ndarray
# """
#
# POINTER_GAMUT_BOUNDARIES = xy_to_XYZ(POINTER_GAMUT_BOUNDARIES)
# """
# Pointer's Gamut boundaries data converted to *CIE XYZ* tristimulus values.
#
# POINTER_GAMUT_BOUNDARIES : ndarray
# """


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
        **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'IPT', 'Hunter Lab', 'Hunter Rdab'}**,
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

    points = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(POINTER_GAMUT_DATA, POINTER_GAMUT_ILLUMINANT,
                                 reference_colourspace), reference_colourspace)

    RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba
    RGB_e = ColorArray(uniform_edge_colour, alpha=uniform_edge_opacity).rgba

    markers = Symbol(
        symbol='cross',
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
        See :func:`pointer_gamut_visual` argument for possible values.

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

    XYZ = np.vstack([POINTER_GAMUT_BOUNDARIES,
                     POINTER_GAMUT_BOUNDARIES[0, ...]])

    illuminant = DEFAULT_PLOTTING_ILLUMINANT

    points = colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(XYZ, illuminant, reference_colourspace),
        reference_colourspace)
    points[np.isnan(points)] = 0

    RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

    line = Line(points, RGB, width=width, method='agg', parent=parent)

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
        See :func:`pointer_gamut_visual` argument for possible values.

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
        points = colourspace_model_axis_reorder(
            XYZ_to_colourspace_model(
                np.vstack([pointer_gamut_data[i],
                           pointer_gamut_data[i][0, ...]]),
                POINTER_GAMUT_ILLUMINANT, reference_colourspace),
            reference_colourspace)

        points[np.isnan(points)] = 0

        RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

        Line(points, RGB, width=width, parent=node)
    return node
