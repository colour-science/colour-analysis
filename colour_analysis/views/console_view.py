#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Console View
============

Defines the *Console View* related objects:

-   :class:`ConsoleView`
"""

from __future__ import division, unicode_literals

from vispy.scene.widgets import Console

from colour import message_box

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2016 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['ConsoleView']


class ConsoleView(Console):
    """
    Defines the *Console View*.

    Parameters
    ----------
    scene_canvas : SceneCanvas, optional
        Current `vispy.scene.SceneCanvas` instance.
    \*args : list, optional
        Arguments passed to :class:`vispy.scene.widgets.Console` class
        constructor.
    \**kwargs : dict, optional
        Keywords arguments passed to :class:`vispy.scene.widgets.Console`
        class constructor.

    Attributes
    ----------
    scene_canvas

    Methods
    -------
    describe_actions_action
    describe_analysis_state_action
    """

    def __init__(self, scene_canvas=None, *args, **kwargs):
        Console.__init__(self, *args, **kwargs)

        self.unfreeze()

        self._scene_canvas = scene_canvas

        self.write('Welcome to Colour - Analysis!\n')

    @property
    def scene_canvas(self):
        """
        Property for **self.scene_canvas** attribute.

        Returns
        -------
        SceneCanvas
        """

        return self._scene_canvas

    @scene_canvas.setter
    def scene_canvas(self, value):
        """
        Setter for **self.scene_canvas** attribute.

        Parameters
        ----------
        value : SceneCanvas
            Attribute value.
        """

        raise AttributeError(
            '"{0}" attribute is read only!'.format('scene_canvas'))

    def describe_actions_action(self):
        """
        Defines the slot triggered by the *describe_actions* action.

        Returns
        -------
        bool
            Definition success.
        """

        actions = ['Actions & Shortcuts\n']
        for _name, action in sorted(self.canvas.actions.items()):
            if action.sequence.modifiers:
                sequence = '{0} + {1}'.format(
                    ' + '.join(action.sequence.modifiers),
                    action.sequence.key)
            else:
                sequence = '{0}'.format(action.sequence.key)
            actions.append('- {0}: {1}'.format(action.description, sequence))

        actions = '\n'.join(actions)

        self.write('{0}'.format(actions))

        message_box('{0}'.format(actions))

        return True

    def describe_analysis_state_action(self):
        """
        Defines the slot triggered by the *describe_analysis_state* action.

        Returns
        -------
        bool
            Definition success.
        """

        state = ['Analysis State\n']

        state.append('- Input image: {0}'.format(
            self.canvas.image_path))
        state.append('- Input RGB colourspace: {0}'.format(
            self.canvas.input_colourspace))
        state.append('- Input OECF: {0}'.format(
            self.canvas.input_oecf))
        state.append('- Input linearity: {0}'.format(
            self.canvas.input_linear))
        state.append('- Reference colourspace: {0}'.format(
            self.canvas.reference_colourspace))
        state.append('- Correlate RGB colourspace: {0}'.format(
            self.canvas.correlate_colourspace))
        state.append('- Blacks Clamped: {0}'.format(
            self.canvas.clamp_blacks))
        state.append('- Whites Clamped: {0}'.format(
            self.canvas.clamp_whites))
        state = '\n'.join(state)

        self.write('{0}'.format(state))

        message_box('{0}'.format(state))

        return True
