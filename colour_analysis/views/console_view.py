#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.scene.widgets import Console

from colour import message_box


class ConsoleView(Console):
    def __init__(self, canvas=None, *args, **kwargs):
        Console.__init__(self, *args, **kwargs)

        self.__canvas = canvas

        self.write('Welcome to Colour - Analysis!\n')

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

    def describe_actions_action(self):
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
        state = '\n'.join(state)

        self.write('{0}'.format(state))

        message_box('{0}'.format(state))

        return True
