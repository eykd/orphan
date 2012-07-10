# -*- coding: utf-8 -*-
"""orphan.terrain -- Features and structures.
"""
from . import enum


class terrain(object):
    __metaclass__ = enum.Enum

    background = 'black'
    foreground = 'light gray'


class empty(terrain):
    glyph = u'  '


class wall(terrain):
    glyph = u'##'


class water(terrain):
    glyph = u'~^'
    foreground = 'light cyan'
    background = 'dark blue'
