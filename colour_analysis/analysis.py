# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
import os

from vispy.scene import SceneCanvas
from vispy.scene.cameras import PanZoomCamera, TurntableCamera

from colour import RGB_COLOURSPACES, read_image

from colour_analysis.common import REFERENCE_COLOURSPACES
from colour_analysis.visuals import (
    RGB_colourspace_gamut_visual,
    RGB_scatter_visual,
    axis_visual,
    image_visual,
    spectral_locus_visual)

RESOURCES_DIRECTORY = os.path.join(os.path.dirname(__file__), 'resources')
IMAGES_DIRECTORY = os.path.join(RESOURCES_DIRECTORY, 'images')
DEFAULT_IMAGE = os.path.join(IMAGES_DIRECTORY, 'Digital_LAD_2048x1556.exr')


class Analysis(SceneCanvas):
    def __init__(self,
                 image_path,
                 input_colourspace,
                 input_oecf,
                 reference_colourspace,
                 correlate_colourspace):
        SceneCanvas.__init__(self,
                             keys='interactive',
                             title="Colour - Analysis")

        self.__image_path = None
        self.image_path = image_path or DEFAULT_IMAGE
        self.__input_colourspace = None
        self.input_colourspace = input_colourspace
        self.__input_oecf = None
        self.input_oecf = input_oecf
        self.__reference_colourspace = None
        self.reference_colourspace = reference_colourspace
        self.__correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace

        self.__image = None
        # self.image = read_image(image_path)
        import skimage.data

        self.image = skimage.data.lena() / 255

        self.__grid = None
        self.__gamut_view = None
        self.__diagram_view = None
        self.__image_view = None

        self.__input_colourspace_visual = None
        self.__correlate_colourspace_visual = None
        self.__spectral_locus_visual = None
        self.__RGB_scatter_visual = None
        self.__axis_visual = None

        self.__image_visual = None

        self.initialise_views()
        self.initialise_visuals()
        self.initialise_cameras()

        self.show()

    @property
    def image_path(self):
        """
        Property for **self.__image_path** private attribute.

        Returns
        -------
        unicode
            self.__image_path.
        """

        return self.__image_path

    @image_path.setter
    def image_path(self, value):
        """
        Setter for **self.__image_path** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert os.path.exists(value), (
                '"{0}" input image doesn\'t exists!'.format('image_path',
                                                            value))
        self.__image_path = value

    @property
    def input_colourspace(self):
        """
        Property for **self.__input_colourspace** private attribute.

        Returns
        -------
        unicode
            self.__input_colourspace.
        """

        return self.__input_colourspace

    @input_colourspace.setter
    def input_colourspace(self, value):
        """
        Setter for **self.__input_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('input_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(
                value, ', '.join(sorted(RGB_COLOURSPACES.keys())))
        self.__input_colourspace = value

    @property
    def input_oecf(self):
        """
        Property for **self.__input_oecf** private attribute.

        Returns
        -------
        unicode
            self.__input_oecf.
        """

        return self.__input_oecf

    @input_oecf.setter
    def input_oecf(self, value):
        """
        Setter for **self.__input_oecf** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('input_oecf', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" OECF is not associated with any factory '
                'RGB colourspaces: "{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self.__input_oecf = value

    @property
    def reference_colourspace(self):
        """
        Property for **self.__reference_colourspace** private attribute.

        Returns
        -------
        unicode
            self.__reference_colourspace.
        """

        return self.__reference_colourspace

    @reference_colourspace.setter
    def reference_colourspace(self, value):
        """
        Setter for **self.__reference_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('reference_colourspace', value))
            assert value in REFERENCE_COLOURSPACES, (
                '"{0}" reference colourspace not found in factory reference '
                'colourspaces: "{1}".').format(
                value, ', '.join(sorted(REFERENCE_COLOURSPACES.keys())))
        self.__reference_colourspace = value

    @property
    def correlate_colourspace(self):
        """
        Property for **self.__correlate_colourspace** private attribute.

        Returns
        -------
        unicode
            self.__correlate_colourspace.
        """

        return self.__correlate_colourspace

    @correlate_colourspace.setter
    def correlate_colourspace(self, value):
        """
        Setter for **self.__correlate_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('correlate_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self.__correlate_colourspace = value

    @property
    def image(self):
        """
        Property for **self.__image** private attribute.

        Returns
        -------
        array_like
            self.__image.
        """

        return self.__image

    @image.setter
    def image(self, value):
        """
        Setter for **self.__image** private attribute.

        Parameters
        ----------
        value : array_like
            Attribute value.
        """

        if value is not None:
            assert type(value) in (tuple, list, np.ndarray, np.matrix), (
                ('"{0}" attribute: "{1}" type is not "tuple", "list", '
                 '"ndarray" or "matrix"!').format('image', value))
        self.__image = value

    def initialise_views(self):
        self.__grid = self.central_widget.add_grid()

        self.__gamut_view = self.__grid.add_view(row=0, col=0, col_span=2)
        self.__gamut_view.border_color = (0.5, 0.5, 0.5, 1)

        self.__diagram_view = self.__grid.add_view(row=1, col=0)
        self.__diagram_view.border_color = (0.5, 0.5, 0.5, 1)

        self.__image_view = self.__grid.add_view(row=1, col=1)
        self.__image_view.border_color = (0.5, 0.5, 0.5, 1)

    def initialise_visuals(self):
        # Gamut View.
        self.__input_colourspace_visual = RGB_colourspace_gamut_visual(
            colourspace=self.__input_colourspace,
            reference_colourspace=self.__reference_colourspace,
            parent=self.__gamut_view.scene)

        self.__correlate_colourspace_visual = RGB_colourspace_gamut_visual(
            colourspace=self.__correlate_colourspace,
            reference_colourspace=self.__reference_colourspace,
            parent=self.__gamut_view.scene)

        self.__spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=self.__reference_colourspace,
            parent=self.__gamut_view.scene)

        self.__RGB_scatter_visual = RGB_scatter_visual(
            self.__image,
            reference_colourspace=self.__reference_colourspace,
            parent=self.__gamut_view)

        self.__axis_visual = axis_visual(parent=self.__gamut_view.scene)

        # Diagram View.

        # Image View.
        # TODO: Remove rotation whenever
        # https://github.com/vispy/vispy/issues/904 is addressed.
        self.__image_visual = image_visual(
            np.rot90(self.__image, 2), parent=self.__image_view.scene)

    def initialise_cameras(self):
        self.__gamut_view.camera = TurntableCamera(fov=45, up='+z')

        self.__diagram_view.camera = PanZoomCamera(aspect=1)

        self.__image_view.camera = PanZoomCamera(aspect=1)