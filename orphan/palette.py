# -*- coding: utf-8 -*-
"""orphan.palette -- color definitions

name -- new entry/attribute name
foreground -- a string containing a comma-separated foreground 
    color and settings
 
    Color values:
    'default' (use the terminal's default foreground),
    'black', 'dark red', 'dark green', 'brown', 'dark blue',
    'dark magenta', 'dark cyan', 'light gray', 'dark gray',
    'light red', 'light green', 'yellow', 'light blue', 
    'light magenta', 'light cyan', 'white'
 
    Settings:
    'bold', 'underline', 'blink', 'standout'
 
    Some terminals use 'bold' for bright colors.  Most terminals
    ignore the 'blink' setting.  If the color is not given then
    'default' will be assumed. 
 
background -- a string containing the background color
 
    Background color values:
    'default' (use the terminal's default background),
    'black', 'dark red', 'dark green', 'brown', 'dark blue',
    'dark magenta', 'dark cyan', 'light gray'
 
mono -- a comma-separated string containing monochrome terminal 
    settings (see "Settings" above.)
 
    None = no terminal settings (same as 'default')
 
foreground_high -- a string containing a comma-separated 
    foreground color and settings, standard foreground
    colors (see "Color values" above) or high-colors may 
    be used
 
    High-color example values:
    '#009' (0% red, 0% green, 60% red, like HTML colors)
    '#fcc' (100% red, 80% green, 80% blue)
    'g40' (40% gray, decimal), 'g#cc' (80% gray, hex),
    '#000', 'g0', 'g#00' (black),
    '#fff', 'g100', 'g#ff' (white)
    'h8' (color number 8), 'h255' (color number 255)
 
    None = use foreground parameter value
 
background_high -- a string containing the background color,
    standard background colors (see "Background colors" above)
    or high-colors (see "High-color example values" above)
    may be used
 
    None = use background parameter value

"""
import re
from collections import namedtuple

fg_colors = set([
    'default',
    'black', 'dark red', 'dark green', 'brown', 'dark blue',
    'dark magenta', 'dark cyan', 'light gray', 'dark gray',
    'light red', 'light green', 'yellow', 'light blue', 
    'light magenta', 'light cyan', 'white'
    ])

bg_colors = set([
    'default',
    'black', 'dark red', 'dark green', 'brown', 'dark blue',
    'dark magenta', 'dark cyan', 'light gray'
    ])

settings = set(['bold', 'underline', 'blink', 'standout'])


_Foreground = namedtuple('Foreground', 'high low mono')


def Foreground(high, low=None, mono=None):
    if low is None:
        if high in fg_colors:
            low = high
        else:
            low = 'default'
    return _Foreground(high, low, mono)


_Background = namedtuple('Background', 'high low')


def Background(high, low=None):
    if low is None:
        if high in bg_colors:
            low = high
        else:
            low = 'default'
    return _Background(high, low)


PaletteEntry = namedtuple(
    'PaletteEntry',
    'name foreground background mono foreground_high background_high')


non_slug_cp = re.compile(r'[^a-zA-Z0-9]')
underscores_cp = re.compile(r'_+')
slug_tr = (
    ('#', 'z',),
    ('(', 'K'),
    (')', 'J'),
    )


def _slugify(s):
    s = str(s).lower()
    for search, replace in slug_tr:
        s = s.replace(search, replace)
    s = non_slug_cp.sub('_', s)
    s = underscores_cp.sub('_', s)
    return s


def as_name(fg_slug, bg_slug):
    return 'p_%s_%s' % (fg_slug, bg_slug)


class Palette(object):
    def __init__(self, defaults=(), foregrounds=(), backgrounds=()):
        self.defaults = defaults
        self.foregrounds = {}
        self.backgrounds = {}

    def __iter__(self):
        for entry in self.defaults:
            yield entry

        for bg_slug, (bg_high, bg) in self.backgrounds.iteritems():
            for fg_slug, (fg_high, fg, mono) in self.foregrounds.iteritems():
                yield PaletteEntry(
                    name = 'p_%s_%s' % (fg_slug, bg_slug),
                    foreground = fg,
                    background = bg,
                    mono = mono,
                    foreground_high = fg_high,
                    background_high = bg_high,
                    )
            
    def registerForeground(self, foreground_high, foreground=None,
                           monochrome=None):
        if isinstance(foreground_high, _Foreground):
            fg = foreground_high
        else:
            fg = Foreground(foreground_high, foreground, monochrome)
        slug = _slugify(fg.high)
        self.foregrounds[slug] = fg
        return slug

    def registerBackground(self, background_high, background=None):
        if isinstance(background_high, _Background):
            bg = background_high
        else:
            bg = Background(background_high, background)
        slug = _slugify(bg.high)
        self.backgrounds[slug] = bg
        return slug


entries = Palette(defaults=[
    # (name, foreground, background, mono, foreground_high, background_high)
    ('player', 'light blue', 'light gray', 'standout'),
    ('wall', 'black', 'light gray'),

    ('body', 'black', 'light gray', 'standout'),
    ('reverse', 'light gray', 'black'),
    ('header', 'white', 'dark red', 'bold'),
    ('important', 'dark blue', 'light gray', ('standout', 'underline')),
    ('editfc', 'white', 'dark blue', 'bold'),
    ('editbx', 'light gray', 'dark blue'),
    ('editcp', 'black', 'light gray', 'standout'),
    ('bright', 'dark gray', 'light gray', ('bold', 'standout')),
    ('buttn', 'black', 'dark cyan'),
    ('buttnf', 'white', 'dark blue', 'bold'),
    ])
