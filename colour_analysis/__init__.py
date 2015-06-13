#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Colour - Analysis
=================

*Colour - Analysis* is a *Python* colour science package dedicated to image
analysis.
"""

from __future__ import absolute_import

import sys

if sys.version_info[0] >= 3:
    # Python 3 compatibility hacks.
    import builtins
    import itertools
    import functools

    builtins.basestring = str
    builtins.unicode = str
    builtins.reduce = functools.reduce
    itertools.izip = zip

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__application_name__ = 'Colour - Analysis'

__major_version__ = '0'
__minor_version__ = '1'
__change_version__ = '0'
__version__ = '.'.join((__major_version__,
                        __minor_version__,
                        __change_version__))

from .analysis import ColourAnalysis

__all__ = ['ColourAnalysis']
