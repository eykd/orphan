# -*- coding: utf-8 -*-
"""orphan.entities -- mobs and other active critters.
"""
from . import enum


class entities(object):
    __metaclass__ = enum.Enum

    foreground = 'light gray'


class empty(entities):
    glyph = '  '


class player(entities):
    glyph = u'子'  # 'Offspring'. Or 孤 'Orphan'?
    foreground = 'light blue'


class adult(entities):
    pass


class child(entities):
    pass


class orphan(entities):
    glyph = u'孤'
