# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Constants
=========

Defines the various constants used in *Colour - Analysis*.
"""

from __future__ import division, unicode_literals

import numpy as np
import os
import scipy.ndimage

from colour import COLOURSPACE_MODELS_LABELS, ILLUMINANTS

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2017 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['RESOURCES_DIRECTORY',
           'SETTINGS_FILE',
           'IMAGES_DIRECTORY',
           'DEFAULT_IMAGE_PATH',
           'DEFAULT_FAILSAFE_IMAGE',
           'DEFAULT_ENCODING_CCTF',
           'DEFAULT_PLOTTING_ILLUMINANT',
           'REFERENCE_COLOURSPACES',
           'REFERENCE_COLOURSPACES_TITLES',
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

DEFAULT_IMAGE_PATH = os.path.join(IMAGES_DIRECTORY,
                                  'Digital_LAD_2048x1556.exr')
"""
Default image path if not is provided on startup.

DEFAULT_IMAGE_PATH : unicode
"""

DEFAULT_FAILSAFE_IMAGE = scipy.ndimage.gaussian_filter(
    (np.random.random((256, 256, 3)) - 0.1) * 1.25, sigma=0.4)
"""
Default failsafe image in case *OpenImageIO* is not available.

DEFAULT_FAILSAFE_IMAGE : ndarray
"""

DEFAULT_ENCODING_CCTF = 'sRGB'
"""
Default display OECF.

DEFAULT_ENCODING_CCTF : unicode
    **{'Rec. 709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
    'ALEXA Wide Gamut RGB', 'Adobe RGB (1998)', 'Adobe Wide Gamut RGB',
    'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
    'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
    'Don RGB 4', 'ECI RGB v2', 'ERIMM RGB', 'Ekta Space PS 5', 'Max RGB',
    'NTSC RGB', 'Pal/Secam RGB', 'ProPhoto RGB', 'REDcolor', 'REDcolor2',
    'REDcolor3', 'REDcolor4', 'RIMM RGB', 'ROMM RGB', 'Rec. 2020',
    'Russell RGB', 'S-Gamut', 'S-Gamut3', 'S-Gamut3.Cine', 'SMPTE-C RGB',
    'V-Gamut', 'Xtreme RGB', 'sRGB'}**
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
# 'CIE LCHab',
    'CIE Luv',
# 'CIE LCHuv',
    'CIE UCS',
    'CIE UVW',
    'IPT',
    'Hunter Lab',
    'Hunter Rdab')
"""
Reference colourspaces defining available colour transformations.

REFERENCE_COLOURSPACES : dict
    **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
    'IPT', 'Hunter Lab', 'Hunter Rdab'}**
"""

REFERENCE_COLOURSPACES_TITLES = COLOURSPACE_MODELS_LABELS
"""
Reference colourspaces to labels mapping.

REFERENCE_COLOURSPACES_TITLES : dict
    **{'CIE XYZ', 'CIE xyY', 'CIE Lab', 'CIE LCHab, 'CIE Luv', 'CIE LCHuv',
    'CIE UCS', 'CIE UVW', 'IPT', 'Hunter Lab', 'Hunter Rdab'}**
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
