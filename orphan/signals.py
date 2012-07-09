# -*- coding: utf-8 -*-
"""signals.py --
"""
from blinker import signal

keyboard = signal('keyboard')
player_actions = signal('player')

block_update = signal('block_update')
