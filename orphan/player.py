# -*- coding: utf-8 -*-
"""orphan.player -- 
"""
import logging
logger = logging.getLogger('player')

import urwid

from . import signals


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
