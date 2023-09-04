# -*- coding: utf-8 -*-
"""
Colour - Analysis
=================

*Colour - Analysis* is a *Python* colour science package dedicated to image
analysis.
"""

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__application_name__ = "Colour - Analysis"

__major_version__ = "0"
__minor_version__ = "1"
__change_version__ = "0"
__version__ = ".".join(
    (__major_version__, __minor_version__, __change_version__)
)

from .analysis import ColourAnalysis

__all__ = ["ColourAnalysis"]
