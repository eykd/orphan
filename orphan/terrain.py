# -*- coding: utf-8 -*-
"""orphan.terrain -- Features and structures.
"""
import itertools as it
from time import time
from noise import pnoise2
import rlfl
from . import enum

from . import util

from . import palette


class terrain(object):
    __metaclass__ = enum.Enum

    flags = None
    clear_flags = None

    background = 'black'
    foreground = 'light gray'

    @classmethod
    def text(cls, at):
        return (palette.as_name(cls.foreground_slug(at)
                                if callable(cls.foreground_slug)
                                else cls.foreground_slug,

                                cls.background_slug(at)
                                if callable(cls.background_slug)
                                else cls.background_slug),

                cls.glyph(at) if callable(cls.glyph) else cls.glyph
                )


class empty(terrain):
    glyph = u'  '
    flags = rlfl.CELL_OPEN | rlfl.CELL_WALK


class dirt(terrain):
    glyphs = [u'%s%s' % i for i in it.permutations([u'∴', u'∵', u'∶', u'∷', u' ', u' '], 2)]
    backgrounds = ['g%s' % x for x in xrange(100)]
    foreground = 'brown'
    flags = rlfl.CELL_OPEN | rlfl.CELL_WALK
    cache = {}
    
    @classmethod
    def background_slug(cls, at):
        return cls.background_slugs[at.height]

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
    foreground = 'light cyan'
    background = 'dark blue'

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
