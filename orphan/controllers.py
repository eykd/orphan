# -*- coding: utf-8 -*-
"""controllers.py -- Orphan controllers.
"""
import logging
logger = logging.getLogger('controllers')

import collections

import urwid

from . import views
from . import signals
from . import agents


class Scene(agents.Agent):
    main_widget = None
    
    def on_enter(self):
        pass

    def on_exit(self):
        pass


class Director(agents.Agent):
    def __init__(self):
        super(Director, self).__init__()
        self.scene_stack = collections.deque()
        self.scene = None
        self.next_scene = None

    def push(self, scene):
        self.next_scene = scene
        if self.scene is not None:
            self.scene_stack.append(self.scene)

    def pop(self, scene):
        if len(self.scene_stack) == 0:
            raise urwid.ExitMainLoop()
        else:
            self.next_scene = self.scene_stack.pop()

    def replace(self, scene):
        self.next_scene = scene

    def _set_scene(self):
        assert self.next_scene is not None
        scene = self.next_scene
        self.next_scene = None

        # always true except for first scene in the app
        if self.scene is not None:
            self.scene.on_exit()

        old = self.scene
        self.scene = scene

        # always true except when terminating the app
        if self.scene is not None:
            scene.on_enter()

        return old

    def schedule_agent(self, loop, data):
        try:
            self.iterator.next()
        except StopIteration:
            return
        else:
            self.loop.set_alarm_in(0.01, self.schedule_agent)

    def run(self, initial_scene):
        logger.info('Director starting up.')
        self.push(initial_scene)
        self._set_scene()

        screen = self.screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(colors=256)
        urwid.set_encoding("UTF-8")

        def unhandled(key):
            logger.debug('Received key sequence: %s', key)
            signals.keyboard.send(key=key)

            # FIXME: This shouldn't be hard-coded here. Rely on scene popping.
            if key in 'qQxX' or key == 'esc':
                logger.info('Director quitting.')
                raise urwid.ExitMainLoop()

        self.loop = urwid.MainLoop(
            self.scene.main_frame, views.palette, screen,
            unhandled_input=unhandled)

        self.iterator = iter(self)
        self.loop.set_alarm_in(0.01, self.schedule_agent)
        self.loop.run()
