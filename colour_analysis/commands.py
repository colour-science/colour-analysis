# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import argparse
import functools
import sys
import traceback
from vispy.app import run

from colour_analysis.analysis import Analysis


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
             [--reference-colourspace REFERENCE_COLOURSPACE]
             [--correlate-colourspace CORRELATE_COLOURSPACE]

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
    -c, --input-colourspace, 'Rec. 709'
        Input image colourspace.
    -f, --input-oecf, None
        Input image colourspace.
    -r, --reference-colourspace, 'CIE xyY'
        Input image colourspace.
    -l, --correlate-colourspace, ['ACEScg']
        Correlate colourspace.

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
                        default=None,
                        help='Input image colourspace.')

    parser.add_argument('--reference-colourspace',
                        '-r',
                        action='store',
                        dest='reference_colourspace',
                        default='CIE xyY',
                        help='Input image colourspace.')

    parser.add_argument('--correlate-colourspace',
                        '-l',
                        action='store',
                        dest='correlate_colourspace',
                        default='ACEScg',
                        help='Correlate colourspace.')

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
    Analysis(arguments.input_image,
             arguments.input_colourspace,
             arguments.input_oecf,
             arguments.reference_colourspace,
             arguments.correlate_colourspace)
    return run()


if __name__ == '__main__':
    main()