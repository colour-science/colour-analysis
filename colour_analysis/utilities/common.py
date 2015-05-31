# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from colour import (
    CMFS,
    Lab_to_LCHab,
    Luv_to_LCHuv,
    Luv_to_uv,
    Luv_uv_to_xy,
    RGB_COLOURSPACES,
    tsplit,
    tstack,
    UCS_to_uv,
    UCS_uv_to_xy,
    xy_to_XYZ,
    XYZ_to_IPT,
    XYZ_to_Lab,
    XYZ_to_Luv,
    XYZ_to_UCS,
    XYZ_to_UVW,
    XYZ_to_xy,
    XYZ_to_xyY)

from colour_analysis.constants import REFERENCE_COLOURSPACES

CHROMATICITY_DIAGRAM_TRANSFORMATIONS = {
    'CIE 1931': {'XYZ_to_ij': lambda a, i: XYZ_to_xy(a, i),
                 'ij_to_XYZ': lambda a, i: xy_to_XYZ(a)},
    'CIE 1960 UCS': {'XYZ_to_ij': lambda a, i: UCS_to_uv(XYZ_to_UCS(a)),
                     'ij_to_XYZ': lambda a, i: xy_to_XYZ(UCS_uv_to_xy(a))},
    'CIE 1976 UCS': {'XYZ_to_ij': lambda a, i: Luv_to_uv(XYZ_to_Luv(a, i), i),
                     'ij_to_XYZ': lambda a, i: xy_to_XYZ(Luv_uv_to_xy(a))}}


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
        **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE Luv uv', 'CIE UCS',
        'CIE UCS uv', 'CIE UVW', 'IPT'}**

        Reference colourspace to convert the *CIE XYZ* tristimulus values to.

    Returns
    -------
    ndarray
        Reference colourspace values.
    """

    value = None
    if reference_colourspace == 'CIE XYZ':
        value = XYZ
    if reference_colourspace == 'CIE xyY':
        value = XYZ_to_xyY(XYZ, illuminant)
    if reference_colourspace == 'CIE Lab':
        L, a, b = tsplit(XYZ_to_Lab(XYZ, illuminant))
        value = tstack((a, b, L))
    if reference_colourspace == 'CIE LCHab':
        L, CH, ab = tsplit(Lab_to_LCHab(XYZ_to_Lab(XYZ, illuminant)))
        value = tstack((CH, ab, L))
    if reference_colourspace == 'CIE Luv':
        L, u, v = tsplit(XYZ_to_Luv(XYZ, illuminant))
        value = tstack((u, v, L))
    if reference_colourspace == 'CIE Luv uv':
        u, v = tsplit(Luv_to_uv(XYZ_to_Luv(XYZ, illuminant), illuminant))
        value = tstack((u, v))
    if reference_colourspace == 'CIE LCHuv':
        L, CH, uv = tsplit(Luv_to_LCHuv(XYZ_to_Luv(XYZ, illuminant)))
        value = tstack((CH, uv, L))
    if reference_colourspace == 'CIE UCS':
        value = XYZ_to_UCS(XYZ)
    if reference_colourspace == 'CIE UCS uv':
        u, v = tsplit(UCS_to_uv(XYZ_to_UCS(XYZ)))
        value = tstack((u, v))
    if reference_colourspace == 'CIE UVW':
        value = XYZ_to_UVW(XYZ * 100, illuminant)
    if reference_colourspace == 'IPT':
        I, P, T = tsplit(XYZ_to_IPT(XYZ))
        value = tstack((P, T, I))

    if value is None:
        raise ValueError(
            ('"{0}" not found in reference colourspace models: '
             '"{1}".').format(reference_colourspace,
                              ', '.join(REFERENCE_COLOURSPACES)))
    return value


def nodes_walker(node, ascendants=False):
    attribute = "children" if not ascendants else "parent"
    if not hasattr(node, attribute):
        return

    elements = getattr(node, attribute)
    elements = elements if isinstance(elements, list) else [elements]

    for element in elements:
        yield element

        if not hasattr(element, attribute):
            continue

        if not getattr(element, attribute):
            continue

        for sub_element in nodes_walker(element, ascendants=ascendants):
            yield sub_element