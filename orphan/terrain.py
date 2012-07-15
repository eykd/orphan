# -*- coding: utf-8 -*-
"""orphan.terrain -- Features and structures.
"""
from time import time
from noise import pnoise2

from . import enum


class terrain(object):
    __metaclass__ = enum.Enum

    background = 'black'
    foreground = 'light gray'


class empty(terrain):
    glyph = u'  '
    backgrounds = ['g%s' % x for x in xrange(100)]

    @classmethod
    def background_slug(cls, at):
        return cls.backgrounds[at.height]


class wall(terrain):
    glyph = u'##'


class water(terrain):
    glyphs = [u'~^', u'~~', u'~~', u'~^']
    foreground = 'light cyan'
    background = 'dark blue'

    @classmethod
    def glyph(cls, at):
        row, col = at.position
        col_prime = int(
            round(
                abs(
                    (time() * 0.1 + (col * 0.1) + pnoise2(row*0.1, col*0.1)) % 1
                    ) * (len(cls.glyphs) - 1)
                )
            )
        return cls.glyphs[col_prime]
