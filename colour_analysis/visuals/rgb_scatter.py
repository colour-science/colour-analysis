# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RGB Scatter Visual
==================

Defines the *RGB Scatter Visual*:

-   :func:`RGB_scatter_visual`
"""

from __future__ import division, unicode_literals

import numpy as np
from vispy.color.color_array import ColorArray

from colour import RGB_to_XYZ
from colour.constants import DEFAULT_FLOAT_DTYPE
from colour.models import XYZ_to_colourspace_model
from colour.plotting import filter_RGB_colourspaces
from colour.plotting.volume import common_colourspace_model_axis_reorder
from colour.utilities import first_item

from colour_analysis.visuals import Symbol

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2018 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['RGB_scatter_visual']


def RGB_scatter_visual(RGB,
                       colourspace='ITU-R BT.709',
                       reference_colourspace='CIE xyY',
                       symbol='disc',
                       size=4.0,
                       edge_size=0.5,
                       uniform_colour=None,
                       uniform_opacity=1.0,
                       uniform_edge_colour=None,
                       uniform_edge_opacity=1.0,
                       resampling='auto',
                       parent=None):
    """
    Returns a :class:`vispy.scene.visuals.Symbol` class instance representing
    *RGB* data using given symbols.

    Parameters
    ----------
    RGB : array_like
        *RGB* data to draw.
    colourspace : unicode, optional
        **{'ITU-R BT.709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
        'ALEXA Wide Gamut', 'Adobe RGB (1998)', 'Adobe Wide Gamut RGB',
        'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
        'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
        'Don RGB 4', 'ECI RGB v2', 'ERIMM RGB', 'Ekta Space PS 5', 'Max RGB',
        'NTSC', 'Pal/Secam', 'ProPhoto RGB', 'REDcolor', 'REDcolor2',
        'REDcolor3', 'REDcolor4', 'RIMM RGB', 'ROMM RGB', 'ITU-R BT.2020',
        'Russell RGB', 'S-Gamut', 'S-Gamut3', 'S-Gamut3.Cine', 'SMPTE-C RGB',
        'V-Gamut', 'Xtreme RGB', 'sRGB'}**,
        :class:`colour.RGB_Colourspace` class instance name defining the *RGB*
        colourspace of the data to draw.
    reference_colourspace : unicode, optional
        **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'IPT', 'Hunter Lab', 'Hunter Rdab'}**,
        Reference colourspace to use for colour conversions / transformations.
    symbol : unicode, optional
        Symbol type to draw.
    size : numeric, optional
        Symbol size.
    edge_size : numeric, optional
        Symbol edge size.
    uniform_colour : array_like, optional
        Uniform symbol colour.
    uniform_opacity : numeric, optional
        Uniform symbol opacity.
    uniform_edge_colour : array_like, optional
        Uniform symbol edge colour.
    uniform_edge_opacity : numeric, optional
        Uniform symbol edge opacity.
    resampling : numeric or unicode, optional
        Resampling value, if numeric input, one pixel every `resampling`
        argument value will be kept.
    parent : Node, optional
        Parent of the *RGB* scatter visual in the `SceneGraph`.

    Returns
    -------
    Symbol
        *RGB* scatter visual.
    """

    colourspace = first_item(filter_RGB_colourspaces(colourspace).values())

    RGB = np.asarray(RGB)

    if resampling == 'auto':
        resampling = max(int((0.0078125 * np.average(RGB.shape[0:1])) // 2), 1)

        RGB = RGB[::resampling, ::resampling].reshape((-1, 3))

    XYZ = RGB_to_XYZ(RGB, colourspace.whitepoint, colourspace.whitepoint,
                     colourspace.RGB_to_XYZ_matrix)

    points = common_colourspace_model_axis_reorder(
        XYZ_to_colourspace_model(XYZ, colourspace.whitepoint,
                                 reference_colourspace), reference_colourspace)

    points[np.isnan(points)] = 0

    RGB = np.clip(RGB, 0, 1)

    if uniform_colour is None:
        RGB = np.hstack((RGB,
                         np.full((RGB.shape[0], 1), uniform_opacity,
                                 DEFAULT_FLOAT_DTYPE)))
    else:
        RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

    if uniform_edge_colour is None:
        RGB_e = RGB
    else:
        RGB_e = ColorArray(
            uniform_edge_colour, alpha=uniform_edge_opacity).rgba

    markers = Symbol(
        symbol=symbol,
        positions=points,
        size=size,
        edge_size=edge_size,
        face_colour=RGB,
        edge_colour=RGB_e,
        parent=parent)

    return markers
