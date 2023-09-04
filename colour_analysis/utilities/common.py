# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Common Utilities
================

Defines the common utilities objects that don't fall in any specific category.
"""

import numpy as np
from colour import (
    Luv_to_uv,
    Luv_uv_to_xy,
    UCS_to_uv,
    UCS_uv_to_xy,
    XYZ_to_Jzazbz,
    XYZ_to_Luv,
    XYZ_to_OSA_UCS,
    XYZ_to_UCS,
    XYZ_to_xy,
    convert,
    xy_to_XYZ,
)
from colour.utilities import full

from colour_analysis.constants import DEFAULT_FLOAT_DTYPE, DEFAULT_INT_DTYPE

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "METHODS_CHROMATICITY_DIAGRAM",
    "Cycle",
    "XYZ_to_colourspace_model",
    "as_contiguous_array",
    "conform_primitive_dtype",
]

METHODS_CHROMATICITY_DIAGRAM = {
    "CIE 1931": {
        "XYZ_to_ij": lambda a, i: XYZ_to_xy(a),
        "ij_to_XYZ": lambda a, i: xy_to_XYZ(a),
    },
    "CIE 1960 UCS": {
        "XYZ_to_ij": lambda a, i: UCS_to_uv(XYZ_to_UCS(a)),
        "ij_to_XYZ": lambda a, i: xy_to_XYZ(UCS_uv_to_xy(a)),
    },
    "CIE 1976 UCS": {
        "XYZ_to_ij": lambda a, i: Luv_to_uv(XYZ_to_Luv(a, i), i),
        "ij_to_XYZ": lambda a, i: xy_to_XYZ(Luv_uv_to_xy(a)),
    },
}
"""
Chromaticity diagram specific helper conversion objects.

METHODS_CHROMATICITY_DIAGRAM : dict
    **{'CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS'}**
"""


class Cycle(object):
    """
    Defines a cycling array like container where items can be retrieved
    endlessly in a circular way.

    Parameters
    ----------
    items : array_like
        Items to iterate on.

    Examples
    --------
    >>> cycle = Cycle((0, 1, 2))
    >>> cycle.current_item()
    0
    >>> cycle.next_item()
    1
    >>> cycle.next_item()
    2
    >>> cycle.next_item()
    0

    :class:`Cycle` class also implements the iterator protocol, it is important
    to note that when using `next` the first item retrieved is at index 0
    whereas using :meth:`Cycle.next_item` method the first item retrieved is at
    index 1:
    >>> cycle = Cycle((0, 1, 2))
    >>> next(cycle)
    0
    >>> next(cycle)
    1
    >>> next(cycle)
    2
    >>> next(cycle)
    0
    """

    def __init__(self, items):
        self._items = items
        self._index = 0

    def __iter__(self):
        """
        Reimplements :meth:`Object.__iter__` method.

        Return
        ------
        Cycle
        """

        return self

    def next(self):
        """
        Retrieves the item at current internal index and then increments the
        index.

        Return
        ------
        Object
        """

        item = self.current_item()

        self._increment_index()

        return item

    def _increment_index(self):
        """
        Increments the internal index pointing at the current item.
        """

        self._index += 1

        if self._index >= len(self._items):
            self._index = 0

    def current_item(self):
        """
        Returns the item at current internal index and then increments the
        index.

        Return
        ------
        Object
        """

        return self._items[self._index]

    def next_item(self):
        """
        Increments the internal index and then returns the item at index.

        Return
        ------
        Object
        """

        self._increment_index()

        return self.current_item()


def XYZ_to_colourspace_model(XYZ, illuminant, model, **kwargs):
    """
    Converts from *CIE XYZ* tristimulus values to given colourspace model while
    normalising for visual convenience some of the models.

    Parameters
    ----------
    XYZ : array_like
        *CIE XYZ* tristimulus values.
    illuminant : array_like
        *CIE XYZ* tristimulus values *illuminant* *xy* chromaticity
        coordinates.
    model : unicode
        **{'CAM02LCD', 'CAM02SCD', 'CAM02UCS', 'CAM16LCD', 'CAM16SCD',
        'CAM16UCS', 'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS',
        'CIE UVW', 'DIN 99', 'Hunter Lab', 'Hunter Rdab', 'ICTCP', 'IGPGTG',
        'IPT', 'JzAzBz', 'OSA UCS', 'hdr-CIELAB', 'hdr-IPT'}**,
        Colourspace model to convert the *CIE XYZ* tristimulus values to.

    Other Parameters
    ----------------
    \\**kwargs : dict, optional
        Keywords arguments.

    Returns
    -------
    ndarray
        Colourspace model values.
    """

    ijk = convert(XYZ, "CIE XYZ", model, illuminant=illuminant, **kwargs)

    # TODO: ICtCp?
    if model == "JzAzBz":
        ijk /= XYZ_to_Jzazbz([1, 1, 1])[0]
    elif model == "OSA UCS":
        ijk /= XYZ_to_OSA_UCS([1, 1, 1])[0]

    return ijk


def as_float_array(a):
    from colour.utilities import as_float_array

    return as_float_array(a, DEFAULT_FLOAT_DTYPE)


def as_int_array(a):
    from colour.utilities import as_int_array

    return as_int_array(a, DEFAULT_INT_DTYPE)


def as_contiguous_array(a, dtype=DEFAULT_FLOAT_DTYPE):
    return np.ascontiguousarray(a.astype(dtype))


def conform_primitive_dtype(primitive):
    """
    Conform the given primitive to the required dtype.

    Parameters
    ----------
    primitive : array_like
        Primitive to conform to the required dtype.

    Returns
    -------
    tuple
        Conformed primitive.
    """

    vertices, faces, outline = primitive

    return (
        vertices.astype(
            [
                ("position", DEFAULT_FLOAT_DTYPE, (3,)),
                ("uv", DEFAULT_FLOAT_DTYPE, (2,)),
                ("normal", DEFAULT_FLOAT_DTYPE, (3,)),
                ("colour", DEFAULT_FLOAT_DTYPE, (4,)),
            ]
        ),
        faces.astype(DEFAULT_INT_DTYPE),
        outline.astype(DEFAULT_INT_DTYPE),
    )


def append_alpha_channel(a, alpha=1):
    a = np.copy(a)

    return np.hstack([a, full(list(a.shape[:-1]) + [1], alpha, dtype=a.dtype)])
