#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from collections import OrderedDict

from vispy.scene.cameras import PanZoomCamera
from vispy.scene.visuals import GridLines, Text
from vispy.scene.widgets.viewbox import ViewBox

from colour import RGB_COLOURSPACES

from colour_analysis.constants import (
    CHROMATICITY_DIAGRAMS,
    CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE)
from colour_analysis.utilities import Cycle
from colour_analysis.visuals import (
    CIE_1931_chromaticity_diagram,
    CIE_1960_UCS_chromaticity_diagram,
    CIE_1976_UCS_chromaticity_diagram,
    RGB_colourspace_triangle_visual,
    RGB_scatter_visual,
    pointer_gamut_boundaries_visual,
    pointer_gamut_visual,
    spectral_locus_visual)


class DiagramView(ViewBox):
    def __init__(self,
                 canvas=None,
                 image=None,
                 oecf='Rec. 709',
                 input_colourspace='Rec. 709',
                 correlate_colourspace='ACEScg',
                 diagram='CIE 1931',
                 **kwargs):
        ViewBox.__init__(self, **kwargs)

        self.__canvas = canvas

        self.__image = None
        self.image = image
        self.__oecf = None
        self.oecf = oecf
        self.__input_colourspace = None
        self.input_colourspace = input_colourspace
        self.__correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace
        self.__diagram = None
        self.diagram = diagram

        self.__diagrams_cycle = Cycle(CHROMATICITY_DIAGRAMS)

        self.__title_overlay_visual = None

        self.__chromaticity_diagram = None
        self.__spectral_locus_visual = None
        self.__RGB_scatter_visual = None
        self.__input_colourspace_visual = None
        self.__correlate_colourspace_visual = None
        self.__pointer_gamut_visual = None
        self.__pointer_gamut_boundaries_visual = None
        self.__grid_visual = None

        self.__clamp_blacks = False
        self.__clamp_whites = False

        self.__create_visuals()
        self.__attach_visuals()
        self.__create_camera()

        self.__create_title_overlay_visual()
        self.__canvas.events.resize.connect(self.__canvas_resize_event)

    @property
    def canvas(self):
        """
        Property for **self.canvas** attribute.

        Returns
        -------
        SceneCanvas
        """

        return self.__canvas

    @canvas.setter
    def canvas(self, value):
        """
        Setter for **self.canvas** attribute.

        Parameters
        ----------
        value : SceneCanvas
            Attribute value.
        """

        raise AttributeError('"{0}" attribute is read only!'.format('canvas'))

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

    @property
    def oecf(self):
        """
        Property for **self.__oecf** private attribute.

        Returns
        -------
        unicode
            self.__oecf.
        """

        return self.__oecf

    @oecf.setter
    def oecf(self, value):
        """
        Setter for **self.__oecf** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('oecf', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" OECF is not associated with any factory '
                'RGB colourspaces: "{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self.__oecf = value

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
    def diagram(self):
        """
        Property for **self.__diagram** private attribute.

        Returns
        -------
        unicode
            self.__diagram.
        """

        return self.__diagram

    @diagram.setter
    def diagram(self, value):
        """
        Setter for **self.__diagram** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('diagram', value))
            assert value in CHROMATICITY_DIAGRAMS, (
                '"{0}" diagram not found in factory chromaticity diagrams: '
                '"{1}".').format(value, ', '.join(
                sorted(CHROMATICITY_DIAGRAMS.keys())))
        self.__diagram = value

    def __create_RGB_scatter_image(self):
        image = self.__image

        if self.__clamp_blacks:
            image = np.clip(image, 0, np.inf)

        if self.__clamp_whites:
            image = np.clip(image, -np.inf, 1)

        return image

    def __create_chromaticity_diagram_visual(self, diagram='CIE 1931'):
        diagrams = {'CIE 1931': CIE_1931_chromaticity_diagram,
                    'CIE 1960 UCS': CIE_1960_UCS_chromaticity_diagram,
                    'CIE 1976 UCS': CIE_1976_UCS_chromaticity_diagram}

        self.__chromaticity_diagram = diagrams[diagram]()

    def __create_spectral_locus_visual(self):
        self.__spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[self.__diagram]),
            uniform_colour=(0.0, 0.0, 0.0),
            width=2.0,
            method='agg')

    def __create_RGB_scatter_visual(self, RGB):
        self.__RGB_scatter_visual = RGB_scatter_visual(
            RGB,
            symbol='cross',
            reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[self.__diagram]),
            uniform_colour=(0.0, 0.0, 0.0))

    def __create_pointer_gamut_visual(self):
        self.__pointer_gamut_visual = pointer_gamut_visual(
            reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[self.__diagram]),
            uniform_opacity=0.4)

    def __create_pointer_gamut_boundaries_visual(self):
        self.__pointer_gamut_boundaries_visual = (
            pointer_gamut_boundaries_visual(reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[
                    self.__diagram])))

    def __create_input_colourspace_visual(self):
        self.__input_colourspace_visual = RGB_colourspace_triangle_visual(
            self.__input_colourspace,
            self.__diagram,
            uniform_colour=(0.8, 0.0, 0.8))

    def __create_correlate_colourspace_visual(self):
        self.__correlate_colourspace_visual = RGB_colourspace_triangle_visual(
            self.__correlate_colourspace,
            self.__diagram,
            uniform_colour=(0.0, 0.8, 0.8))

    def __create_grid_visual(self):
        self.__grid_visual = GridLines()

    def __create_visuals(self):
        self.__create_chromaticity_diagram_visual(self.__diagram)
        self.__create_spectral_locus_visual()
        self.__create_RGB_scatter_visual(self.__create_RGB_scatter_image())
        self.__create_pointer_gamut_visual()
        self.__create_pointer_gamut_boundaries_visual()
        self.__create_input_colourspace_visual()
        self.__create_correlate_colourspace_visual()
        self.__create_grid_visual()

    def __create_camera(self):
        self.camera = PanZoomCamera(rect=(-0.1, -0.1, 1.1, 1.1),
                                    aspect=1)

    def __attach_visuals(self):
        self.__chromaticity_diagram.add_parent(self.scene)
        self.__spectral_locus_visual.add_parent(self.scene)
        self.__RGB_scatter_visual.add_parent(self.scene)
        self.__pointer_gamut_visual.add_parent(self.scene)
        self.__pointer_gamut_boundaries_visual.add_parent(self.scene)
        self.__input_colourspace_visual.add_parent(self.scene)
        self.__correlate_colourspace_visual.add_parent(self.scene)
        self.__grid_visual.add_parent(self.scene)

    def __detach_visuals(self):
        self.__chromaticity_diagram.remove_parent(self.scene)
        self.__spectral_locus_visual.remove_parent(self.scene)
        self.__RGB_scatter_visual.remove_parent(self.scene)
        self.__pointer_gamut_visual.remove_parent(self.scene)
        self.__pointer_gamut_boundaries_visual.remove_parent(self.scene)
        self.__input_colourspace_visual.remove_parent(self.scene)
        self.__correlate_colourspace_visual.remove_parent(self.scene)
        self.__grid_visual.remove_parent(self.scene)

    def __create_title_overlay_visual(self):
        self.__title_overlay_visual = Text(str(),
                                           anchor_x='center',
                                           anchor_y='bottom',
                                           font_size=10,
                                           color=(0.8, 0.8, 0.8),
                                           parent=self)

        self.__title_overlay_visual_position()
        self.__title_overlay_visual_text()

    def __title_overlay_visual_position(self):
        self.__title_overlay_visual.pos = self.size[0] / 2, 32

    def __title_overlay_visual_text(self):
        title = ''

        if self.__input_colourspace_visual.visible:
            title += self.__input_colourspace
            title += ' - '
        if self.__correlate_colourspace_visual.visible:
            title += self.__correlate_colourspace
            title += ' - '

        title += '{0} Chromaticity Diagram'.format(
            self.__diagrams_cycle.current_item())

        if self.__clamp_blacks:
            title += ' - '
            title += 'Blacks Clamped'

        if self.__clamp_whites:
            title += ' - '
            title += 'Whites Clamped'

        self.__title_overlay_visual.text = title

    def __canvas_resize_event(self, event=None):
        self.__title_overlay_visual_position()

    def __store_visuals_visibility(self):
        visible = OrderedDict()
        visible['chromaticity_diagram_visual'] = (
            self.__chromaticity_diagram.visible)
        visible['spectral_locus_visual'] = (
            self.__spectral_locus_visual.visible)
        visible['RGB_scatter_visual'] = (
            self.__RGB_scatter_visual.visible)
        visible['pointer_gamut_visual'] = (
            self.__pointer_gamut_visual.visible)
        visible['pointer_gamut_boundaries_visual'] = (
            self.__pointer_gamut_boundaries_visual.visible)
        visible['input_colourspace_visual'] = (
            self.__input_colourspace_visual.visible)
        visible['correlate_colourspace_visual'] = (
            self.__correlate_colourspace_visual.visible)
        visible['grid_visual'] = (
            self.__grid_visual.visible)

        self.__visuals_visibility = visible

    def __restore_visuals_visibility(self):
        visible = self.__visuals_visibility

        self.__chromaticity_diagram.visible = (
            visible['chromaticity_diagram_visual'])
        self.__spectral_locus_visual.visible = (
            visible['spectral_locus_visual'])
        self.__RGB_scatter_visual.visible = (
            visible['RGB_scatter_visual'])
        self.__pointer_gamut_visual.visible = (
            visible['pointer_gamut_visual'])
        self.__pointer_gamut_boundaries_visual.visible = (
            visible['pointer_gamut_boundaries_visual'])
        self.__input_colourspace_visual.visible = (
            visible['input_colourspace_visual'])
        self.__correlate_colourspace_visual.visible = (
            visible['correlate_colourspace_visual'])
        self.__grid_visual.visible = (
            visible['grid_visual'])

    def toggle_spectral_locus_visual_visibility_action(self):
        self.__spectral_locus_visual.visible = (
            not self.__spectral_locus_visual.visible)

        return True

    def toggle_input_colourspace_visual_visibility_action(self):
        self.__input_colourspace_visual.visible = (
            not self.__input_colourspace_visual.visible)
        self.__title_overlay_visual_text()

        return True

    def toggle_correlate_colourspace_visual_visibility_action(self):
        self.__correlate_colourspace_visual.visible = (
            not self.__correlate_colourspace_visual.visible)
        self.__title_overlay_visual_text()

        return True

    def toggle_RGB_scatter_visual_visibility_action(self):
        self.__RGB_scatter_visual.visible = (
            not self.__RGB_scatter_visual.visible)

        return True

    def toggle_pointer_gamut_visual_visibility_action(self):
        self.__pointer_gamut_visual.visible = (
            not self.__pointer_gamut_visual.visible)
        self.__pointer_gamut_boundaries_visual.visible = (
            not self.__pointer_gamut_boundaries_visual.visible)

        return True

    def toggle_grid_visual_visibility_action(self):
        self.__grid_visual.visible = not self.__grid_visual.visible

        return True

    def cycle_correlate_colourspace_action(self):
        self.__detach_visuals()
        self.__create_correlate_colourspace_visual()
        self.__attach_visuals()
        self.__title_overlay_visual_text()

        return True

    def cycle_chromaticity_diagram_action(self):
        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__diagram = self.__diagrams_cycle.next_item()
        self.__create_visuals()
        self.__attach_visuals()
        self.__restore_visuals_visibility()
        self.__title_overlay_visual_text()

        return True

    def toggle_blacks_clamp_action(self):
        self.__clamp_blacks = not self.__clamp_blacks
        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__create_RGB_scatter_visual(self.__create_RGB_scatter_image())
        self.__attach_visuals()
        self.__restore_visuals_visibility()
        self.__title_overlay_visual_text()

        return True

    def toggle_whites_clamp_action(self):
        self.__clamp_whites = not self.__clamp_whites
        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__create_RGB_scatter_visual(self.__create_RGB_scatter_image())
        self.__attach_visuals()
        self.__restore_visuals_visibility()
        self.__title_overlay_visual_text()

        return True
