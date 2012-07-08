# -*- coding: utf-8 -*-
"""signals.py --
"""
from blinker import signal

keyboard = signal('keyboard')
player_actions = signal('player')
