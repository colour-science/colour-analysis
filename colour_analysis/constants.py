# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constants
=========

Defines the various constants used in *Colour - Analysis*.
"""

from __future__ import division, unicode_literals

import os

from colour import ILLUMINANTS

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['RESOURCES_DIRECTORY',
           'SETTINGS_FILE',
           'IMAGES_DIRECTORY',
           'DEFAULT_IMAGE',
           'DEFAULT_PLOTTING_ILLUMINANT',
           'REFERENCE_COLOURSPACES',
           'REFERENCE_COLOURSPACES_TO_LABELS',
           'CHROMATICITY_DIAGRAMS',
           'CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE',
           'LINEAR_IMAGE_FORMATS']

RESOURCES_DIRECTORY = os.path.join(os.path.dirname(__file__), 'resources')
"""
Default resources directory.

RESOURCES_DIRECTORY : unicode
"""

SETTINGS_FILE = os.path.join(RESOURCES_DIRECTORY, 'settings.json')
"""
Default *JSON* settings file.

SETTINGS_FILE : unicode
"""

IMAGES_DIRECTORY = os.path.join(RESOURCES_DIRECTORY, 'images')
"""
Default images directory.

IMAGES_DIRECTORY : unicode
"""

DEFAULT_IMAGE = os.path.join(IMAGES_DIRECTORY, 'Digital_LAD_2048x1556.exr')
"""
Default image if not is provided on startup.

DEFAULT_IMAGE : unicode
"""

DEFAULT_PLOTTING_ILLUMINANT = ILLUMINANTS.get(
    'CIE 1931 2 Degree Standard Observer').get('D65')
"""
Illuminant *xy* chromaticity coordinates to use in the various plots.

DEFAULT_PLOTTING_ILLUMINANT : tuple
"""

REFERENCE_COLOURSPACES = (
    'CIE XYZ',
    'CIE xyY',
    'CIE Lab',
    'CIE Luv',
    'CIE UCS',
    'CIE UVW',
    'IPT')
# 'CIE LCHab',
# 'CIE LCHuv',)
"""
Reference colourspaces defining available colour transformations.

REFERENCE_COLOURSPACES : dict
    **{'CIE XYZ', 'CIE xyY', 'CIE Lab', , 'CIE Luv', 'CIE UCS', 'CIE UVW',
    'IPT', 'CIE LCHab', 'CIE LCHuv'}**
"""

REFERENCE_COLOURSPACES_TO_LABELS = {
    'CIE XYZ': ('X', 'Y', 'Z'),
    'CIE xyY': ('x', 'y', 'Y'),
    'CIE Lab': ('a', 'b', '$L^*$'),
    'CIE Luv': ('$u^\prime$', '$v^\prime$', '$L^*$'),
    'CIE UCS': ('U', 'V', 'W'),
    'CIE UVW': ('U', 'V', 'W'),
    'IPT': ('P', 'T', 'I'),
    'CIE LCHab': ('CH', 'ab', '$L^*$'),
    'CIE LCHuv': ('CH', 'uv', '$L^*$')}
"""
Reference colourspaces to labels mapping.

REFERENCE_COLOURSPACES_TO_LABELS : dict
    **{'CIE XYZ', 'CIE xyY', 'CIE Lab', , 'CIE Luv', 'CIE UCS', 'CIE UVW',
    'IPT', 'CIE LCHab', 'CIE LCHuv'}**
"""

CHROMATICITY_DIAGRAMS = ('CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS')
"""
Available chromaticity diagrams.

CHROMATICITY_DIAGRAMS : tuple
"""

CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE = {
    'CIE 1931': 'CIE xy',
    'CIE 1960 UCS': 'CIE UCS uv',
    'CIE 1976 UCS': 'CIE Luv uv'}
"""
Chromaticity diagrams associated colourspace.

CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE : dict
"""

LINEAR_IMAGE_FORMATS = ('.exr', '.hdr')
"""
Assumed linear input image formats.

LINEAR_IMAGE_FORMATS : tuple
"""
