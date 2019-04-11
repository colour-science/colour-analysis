# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Guerilla - Monkey Patching
==========================

Implements various monkey patching related goodness.
"""

from __future__ import division, unicode_literals

from vispy.scene.node import Node


def _Node__visible_getter(self):
    """
    Property for **Node.visible** attribute.

    Returns
    -------
    bool
        self._visible.
    """

    return self._visible


def _Node__visible_setter(self, value):
    """
    Setter for **Node.visible** attribute.

    Parameters
    ----------
    value : bool
        Attribute value.
    """

    for child in [self] + self.children:
        child._visible = value
        child.update()


Node.visible = property(fget=_Node__visible_getter, fset=_Node__visible_setter)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2019 - Colour Developers'
__license__ = 'New BSD License - https://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'
