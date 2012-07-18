# -*- coding: utf-8 -*-
"""orphan.entities -- mobs and other active critters.
"""
from . import enum

# CJK unified ideographs
cjk = [unichr(n) for n in xrange(0x4e00, 0x9fc2)]


class entities(object):
    __metaclass__ = enum.Enum

    foreground = 'light gray'


class empty(entities):
    glyph = '  '


class player(entities):
    glyph = u'子'  # 'Offspring'. Or 孤 'Orphan'?
    foreground = 'yellow'


class adult(entities):
    pass


class child(entities):
    pass


class orphan(entities):
    glyph = u'孤'
