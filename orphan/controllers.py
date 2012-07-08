# -*- coding: utf-8 -*-
"""controllers.py -- Orphan controllers.
"""
import logging
logger = logging.getLogger('controllers')
import urwid

from . import views
from . import models
from . import signals
from . import agents


class PlayerCommandMap(urwid.CommandMap):
    _command_defaults = {
        'up': 'move_north',
        'down': 'move_south',
        'left': 'move_west',
        'right': 'move_east',
    }


class Player(object):
    command_map = PlayerCommandMap()

    def __init__(self, player):
        self.player = player

        @signals.keyboard.connect
        def dispatch_key(sender, key=None):
            action = self.command_map[key]
            if action is not None:
                logger.debug('Dispatching action: %s', action)
                getattr(self.player, action)()

        self._dispatch_key = dispatch_key


class Director(agents.Agent):
    def run(self):
        logger.info('Director starting up.')
        block = models.Block(1000, 1000)
        player = models.Player(block, (20, 20))
        controls = Player(player)

        field = views.PlayField(block, player)
        frame = views.MainFrame(field)

        screen = self.screen = urwid.raw_display.Screen()
        screen.set_terminal_properties(colors=256)
        urwid.set_encoding("UTF-8")

        def unhandled(key):
            logger.debug('Received key sequence: %s', key)
            signals.keyboard.send(key=key)
            field._invalidate()

            if key in 'qQxX' or key == 'esc':
                logger.info('Director quitting.')
                raise urwid.ExitMainLoop()

        self.loop = urwid.MainLoop(
            frame, views.palette, screen,
            unhandled_input=unhandled)

        iterator = iter(self)

        def schedule(loop, data):
            try:
                iterator.next()
            except StopIteration:
                return
            else:
                loop.set_alarm_in(0.01, schedule)
            
        self.loop.set_alarm_in(0.01, schedule)
        self.loop.run()
