# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Commands
========

Defines the command line related objects.
"""

from __future__ import division, unicode_literals

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import argparse
import functools
import json
import traceback
import warnings
from vispy.app import run

from colour_analysis.analysis import ColourAnalysis
from colour_analysis.constants import (
    DEFAULT_IMAGE,
    LINEAR_IMAGE_FORMATS,
    SETTINGS_FILE)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['ManualAction',
           'system_exit',
           'command_line_arguments',
           'main']


class ManualAction(argparse.Action):
    """
    Handles conversion of '-m/--manual' argument in order to provide detailed 
    manual with usage examples.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Reimplements the :meth:`argparse.Action.__call__` method.

        Parameters
        ----------
        parser : object
             Parser.
        namespace : object
             Namespace.
        values : object
             Values.
        option_string : object
             Option string.
        """

        print("""'analysis' Commands Manual
NAME
    analysis -- 'Colour' Image Analysis
SYNOPSIS
    analysis [-v] [-h] [-m] [--input-image INPUT_IMAGE]
             [--input-colourspace INPUT_COLOURSPACE]
             [--input-oecf INPUT_OECF]
             [--input-linearity INPUT_LINEARITY]
             [--input-resample INPUT_DOWNSIZE]
             [--reference-colourspace REFERENCE_COLOURSPACE]
             [--correlate-colourspace CORRELATE_COLOURSPACE]
             [--settings-file SETTINGS_FILE]
             [--layout LAYOUT]
             [--enable-warnings ENABLE_WARNINGS]

DESCRIPTION
    This tool implements various image analysis tools based on 'Colour',
    'Vispy' and 'OpenImageIO'.

ARGUMENTS
    -v, --version
        Displays application release version.
    -h, --help
        Displays this help message and exit. Please use -m/--manual for
        examples.
    -m, --manual
        Displays detailed manual with usage examples.
    -i, --input-image
        Image to analyse.
    -c, --input-colourspace
        {'Rec. 709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
        'ALEXA Wide Gamut RGB', 'Adobe RGB 1998', 'Adobe Wide Gamut RGB',
        'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
        'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
        'Don RGB 4', 'ECI RGB v2', 'Ekta Space PS 5', 'Max RGB', 'NTSC RGB',
        'Pal/Secam RGB', 'ProPhoto RGB', 'REDcolor', 'REDcolor2', 'REDcolor3',
        'REDcolor4', 'Rec. 2020', 'Russell RGB', 'S-Gamut', 'S-Gamut3',
        'S-Gamut3.Cine', 'SMPTE-C RGB', 'V-Gamut', 'Xtreme RGB', 'sRGB'}

        Input image colourspace.
    -f, --input-oecf, None
        Input image OECF, see *input-colourspace* for possible values.
    -l, --input-linearity
        {'auto', 'linear', 'oecf'}

        Input image linearity.
    -z, --input-resample
        Input will be resampled by given factor.
    -r, --reference-colourspace
        {'CIE xyY', 'CIE XYZ', 'CIE Lab', 'CIE Luv', 'CIE UCS', 'CIE UVW',
        'IPT'}

        Input image colourspace.
    -t, --correlate-colourspace
        Correlate colourspace, see *input-colourspace* for possible values.
    -s, --settings-file
        Settings file.
    -y, --layout
        {'layout_1', 'layout_2', 'layout_3', ..., 'layout_n'}

        Application layout.
    -w, --enable-warnings
        Enable warnings.

EXAMPLES
""")

        sys.exit(0)


def system_exit(object):
    """
    Handles proper system exit in case of critical exception.

    Parameters
    ----------
    object : object
        Object to decorate.

    Return
    ------
    object
    """

    @functools.wraps(object)
    def system_exit_wrapper(*args, **kwargs):
        """
        Handles proper system exit in case of critical exception.

        Parameters
        ----------
        \*kwargs : \*
            Arguments.
        \*\*kwargs : \*\*
            Keywords arguments.
        """

        try:
            if object(*args, **kwargs):
                sys.exit()
        except Exception:
            traceback.print_exc()
            sys.exit(1)

    return system_exit_wrapper


def command_line_arguments():
    """
    Returns a command line arguments parser.

    Return
    ------
    ArgumentParser
        Command line arguments parser.
    """

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument('-v',
                        '--version',
                        action='store_true',
                        dest='version',
                        help='Displays application release version.')

    parser.add_argument('-h',
                        '--help',
                        action='help',
                        help=('Displays this help message and exit. Please '
                              'use -m/--manual for examples.'))

    parser.add_argument('-m',
                        '--manual',
                        action=ManualAction,
                        help='Displays detailed manual with usage examples.',
                        nargs=0)

    parser.add_argument('--input-image',
                        '-i',
                        action='store',
                        dest='input_image',
                        default=DEFAULT_IMAGE,
                        help='Image to analyse.')

    parser.add_argument('--input-colourspace',
                        '-c',
                        action='store',
                        dest='input_colourspace',
                        default='Rec. 709',
                        help='Input image colourspace.')

    parser.add_argument('--input-oecf',
                        '-f',
                        action='store',
                        dest='input_oecf',
                        default='Rec. 709',
                        help='Input image OECF.')

    parser.add_argument('--input-linearity',
                        '-l',
                        action='store',
                        dest='input_linearity',
                        default='auto',
                        help='Input image linearity.')

    parser.add_argument('--input-resample',
                        '-z',
                        action='store',
                        dest='input_resample',
                        default=1,
                        help='Input will be resampled by given factor.')

    parser.add_argument('--reference-colourspace',
                        '-r',
                        action='store',
                        dest='reference_colourspace',
                        default='CIE xyY',
                        help='Input image colourspace.')

    parser.add_argument('--correlate-colourspace',
                        '-t',
                        action='store',
                        dest='correlate_colourspace',
                        default='ACEScg',
                        help='Correlate colourspace.')

    parser.add_argument('--settings-file',
                        '-s',
                        action='store',
                        dest='settings_file',
                        default=None,
                        help='Settings file.')

    parser.add_argument('--layout',
                        '-y',
                        action='store',
                        dest='layout',
                        default='layout_1',
                        help='Application layout.')

    parser.add_argument('--enable-warnings',
                        '-w',
                        action='store_true',
                        dest='enable_warnings',
                        default=False,
                        help='Enable warnings.')

    return parser.parse_args()


@system_exit
def main():
    """
    Starts the application.

    Return
    ------
    bool
        Definition success.
    """

    arguments = command_line_arguments()
    settings = json.load(open(SETTINGS_FILE))
    if arguments.settings_file is not None:
        assert os.path.exists(arguments.settings_file), (
            '"{0}" file doesn\'t exists!'.format(arguments.settings_file))
        settings.update(json.load(open(arguments.settings_file)))

    input_linearity = arguments.input_linearity.lower()
    if input_linearity == 'linear':
        input_linear = True
    elif input_linearity == 'oecf':
        input_linear = False
    else:
        input_extension = os.path.splitext(arguments.input_image)[1].lower()
        if input_extension in LINEAR_IMAGE_FORMATS:
            input_linear = True
        else:
            input_linear = False

    if not arguments.enable_warnings:
        warnings.filterwarnings("ignore")

    ColourAnalysis(arguments.input_image,
                   arguments.input_colourspace,
                   arguments.input_oecf,
                   input_linear,
                   int(arguments.input_resample),
                   arguments.reference_colourspace,
                   arguments.correlate_colourspace,
                   settings,
                   arguments.layout)
    return run()


if __name__ == '__main__':
    main()