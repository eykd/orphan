# -*- coding: utf-8 -*-
"""orphan.items -- stuff.
"""
from . import enum


class items(object):
    __metaclass__ = enum.Enum

    foreground = 'black'


class empty(items):
    glyph = '  '
