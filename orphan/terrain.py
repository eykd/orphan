# -*- coding: utf-8 -*-
"""orphan.terrain -- Features and structures.
"""
import itertools as it
from time import time
from noise import pnoise2
import rlfl
from . import enum

from . import util


class terrain(object):
    __metaclass__ = enum.Enum

    flags = None
    clear_flags = None

    background_slug = 'black'
    foreground_slug = 'light gray'


class empty(terrain):
    glyph = u'  '
    foreground_slug = 'dark red'
    backgrounds = ['g%s' % x for x in xrange(100)]
    flags = rlfl.CELL_OPEN | rlfl.CELL_WALK

    @classmethod
    def background_slug(cls, at):
        return cls.backgrounds[at.height]


class dirt(terrain):
    glyphs = [u'%s%s' % i for i in it.permutations([u'∴', u'∵', u'∶', u'∷'], 2)]
    backgrounds = ['g%s' % x for x in xrange(100)]
    flags = rlfl.CELL_OPEN | rlfl.CELL_WALK
    cache = {}
    
    @classmethod
    def background_slug(cls, at):
        return cls.backgrounds[at.height]

    @classmethod
    def glyph(cls, at):
        try:
            return cls.cache[at.position]
        except KeyError:
            row, col = at.position
            col_prime = int(
                round(
                    abs(
                        (pnoise2(row*0.1, col*0.1)) % 1
                        ) * (len(cls.glyphs) - 1)
                    )
                )
            g = cls.cache[at.position] = cls.glyphs[col_prime]
            return g


class wall(terrain):
    glyph = u'##'
    clear_flags = rlfl.CELL_OPEN | rlfl.CELL_WALK


class water(terrain):
    glyphs = [u'~^', u'~~', u'~~', u'~^']
    foreground_slug = 'light cyan'
    background_slug = 'dark blue'

    clear_flags = rlfl.CELL_WALK

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
