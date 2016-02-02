# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Common Utilities
================

Defines common utilities objects that don't fall in any specific category.
"""

from __future__ import division, unicode_literals

from colour import (
    Luv_to_uv,
    Luv_uv_to_xy,
    UCS_to_uv,
    UCS_uv_to_xy,
    xy_to_XYZ,
    XYZ_to_Luv,
    XYZ_to_UCS,
    XYZ_to_xy)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2016 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['CHROMATICITY_DIAGRAM_TRANSFORMATIONS',
           'Cycle']

CHROMATICITY_DIAGRAM_TRANSFORMATIONS = {
    'CIE 1931': {'XYZ_to_ij': lambda a, i: XYZ_to_xy(a, i),
                 'ij_to_XYZ': lambda a, i: xy_to_XYZ(a)},
    'CIE 1960 UCS': {'XYZ_to_ij': lambda a, i: UCS_to_uv(XYZ_to_UCS(a)),
                     'ij_to_XYZ': lambda a, i: xy_to_XYZ(UCS_uv_to_xy(a))},
    'CIE 1976 UCS': {'XYZ_to_ij': lambda a, i: Luv_to_uv(XYZ_to_Luv(a, i), i),
                     'ij_to_XYZ': lambda a, i: xy_to_XYZ(Luv_uv_to_xy(a))}}
"""
Chromaticity diagram specific helper conversion objects.

CHROMATICITY_DIAGRAM_TRANSFORMATIONS : dict
    {'CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS'}
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
        self.__items = items
        self.__index = 0

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

        self.__increment_index()

        return item

    def __increment_index(self):
        """
        Increments the internal index pointing at the current item.
        """

        self.__index += 1

        if self.__index >= len(self.__items):
            self.__index = 0

    def current_item(self):
        """
        Returns the item at current internal index and then increments the
        index.

        Return
        ------
        Object
        """

        return self.__items[self.__index]

    def next_item(self):
        """
        Increments the internal index and then returns the item at index.

        Return
        ------
        Object
        """

        self.__increment_index()

        return self.current_item()
