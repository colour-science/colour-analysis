# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from colour import (
    CMFS,
    ILLUMINANTS,
    RGB_COLOURSPACES,
    XYZ_to_IPT,
    XYZ_to_Lab,
    XYZ_to_Luv,
    XYZ_to_UCS,
    XYZ_to_UVW,
    XYZ_to_xyY,
    tsplit,
    tstack)

DEFAULT_PLOTTING_ILLUMINANT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get('D65')

COLOURSPACE_TO_LABELS = {
    'CIE XYZ': ('X', 'Y', 'Z'),
    'CIE xyY': ('x', 'y', 'Y'),
    'CIE Lab': ('a', 'b', '$L^*$'),
    'CIE Luv': ('$u^\prime$', '$v^\prime$', '$L^*$'),
    'CIE UCS': ('U', 'V', 'W'),
    'CIE UVW': ('U', 'V', 'W'),
    'IPT': ('P', 'T', 'I')}
"""
Colourspace to labels mapping.

COLOURSPACE_TO_LABELS : dict
    **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
    'IPT'}**
"""


def get_RGB_colourspace(colourspace):
    """
    Returns the *RGB* colourspace with given name.

    Parameters
    ----------
    colourspace : unicode
        *RGB* colourspace name.

    Returns
    -------
    RGB_Colourspace
        *RGB* colourspace.

    Raises
    ------
    KeyError
        If the given *RGB* colourspace is not found in the factory *RGB*
        colourspaces.
    """

    colourspace, name = RGB_COLOURSPACES.get(colourspace), colourspace
    if colourspace is None:
        raise KeyError(
            ('"{0}" colourspace not found in factory colourspaces: '
             '"{1}".').format(name, ', '.join(
                sorted(RGB_COLOURSPACES.keys()))))

    return colourspace


def get_cmfs(cmfs):
    """
    Returns the colour matching functions with given name.

    Parameters
    ----------
    cmfs : unicode
        Colour matching functions name.

    Returns
    -------
    RGB_ColourMatchingFunctions or XYZ_ColourMatchingFunctions
        Colour matching functions.

    Raises
    ------
    KeyError
        If the given colour matching functions is not found in the factory
        colour matching functions.
    """

    cmfs, name = CMFS.get(cmfs), cmfs
    if cmfs is None:
        raise KeyError(
            ('"{0}" not found in factory colour matching functions: '
             '"{1}".').format(name, ', '.join(sorted(CMFS.keys()))))
    return cmfs


def XYZ_to_reference_colourspace(XYZ,
                                 illuminant,
                                 reference_colourspace):
    """
    Converts from *CIE XYZ* tristimulus values to given reference colourspace.

    Parameters
    ----------
    XYZ : array_like
        *CIE XYZ* tristimulus values.
    illuminant : array_like
        *CIE XYZ* tristimulus values *illuminant* *xy* chromaticity
        coordinates.
    reference_colourspace : unicode
        **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'IPT'}**

        Reference colourspace to convert the *CIE XYZ* tristimulus values to.

    Returns
    -------
    ndarray
        Reference colourspace values.
    """

    if reference_colourspace == 'CIE XYZ':
        value = XYZ
    if reference_colourspace == 'CIE xyY':
        value = XYZ_to_xyY(XYZ, illuminant)
    if reference_colourspace == 'CIE Lab':
        L, a, b = tsplit(XYZ_to_Lab(XYZ, illuminant))
        value = tstack((a, b, L))
    if reference_colourspace == 'CIE Luv':
        L, u, v = tsplit(XYZ_to_Luv(XYZ, illuminant))
        value = tstack((u, v, L))
    if reference_colourspace == 'CIE UCS':
        value = XYZ_to_UCS(XYZ)
    if reference_colourspace == 'CIE UVW':
        value = XYZ_to_UVW(XYZ * 100, illuminant)
    if reference_colourspace == 'IPT':
        I, P, T = tsplit(XYZ_to_IPT(XYZ))
        value = tstack((P, T, I))

    return value
