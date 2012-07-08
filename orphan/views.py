# -*- coding: utf-8 -*-
"""views.py -- Orphan views.
"""
import logging
logger = logging.getLogger('views')

from collections import defaultdict
import urwid
import urwid.raw_display

from . import signals
from .models import ENTITIES


palette = [
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
    ]


class Camera(object):
    # Use http://www.mandarintools.com/chardict_u8.html for inspiration.
    char_map = defaultdict(lambda: u'??', {
        ENTITIES.empty.index: u'  ',
        ENTITIES.wall.index: ('wall', u'##'),
        ENTITIES.player.index: ('player', u'子'),  # 'Offspring'. Or 孤 'Orphan'?
    })

    def __init__(self, block, focus):
        super(Camera, self).__init__()
        self.block = block
        self.focus = focus

    def render(self, columns, rows):
        # Find the camera's origin
        center_row, center_col = self.focus.position
        max_row, max_col = self.block.shape
        origin_row = min(
            max(center_row - (rows // 2), 0),
            max_row - rows)
        origin_col = min(
            # Displayed columns are double-wide
            max(center_col - (columns // 4), 0),
            max_col - columns)

        logger.debug('Camera: center c/r (%s, %s), origin c/r (%s, %s)',
            center_col, center_row, origin_row, origin_col)

        # Render the camera's view
        block = self.block
        char_map = self.char_map
        Text = urwid.Text
        rendered_rows = []
        for row in xrange(origin_row, (origin_row + rows)):
            row_text = []
            # Displayed columns are double-wide
            for col in xrange(origin_col, (origin_col + (columns // 2))):
                row_text.append(char_map[block[row, col]])
            rendered_rows.append(
                (Text(row_text).render((columns,)), None, None)
                )
        canvas = urwid.CanvasCombine(rendered_rows)
        return canvas


class PlayField(urwid.BoxWidget):
    def __init__(self, block, player):
        super(PlayField, self).__init__()
        self.player = player
        self.camera = Camera(block, player)

    def selectable(self):
        return False

    def render(self, size, focus=False):
        maxcol, maxrow = size
        return self.camera.render(maxcol, maxrow)


class Log(urwid.ListBox):
    def __init__(self):
        self.log = urwid.SimpleListWalker([urwid.Text('Welcome!')])
        super(Log, self).__init__(self.log)

    def selectable(self):
        return False

    def write(self, item):
        self.log.insert(0, urwid.Text(item))

    def close(self):
        pass


class MainFrame(urwid.Frame):
    def __init__(self, main_widget):
        header = urwid.AttrWrap(
            urwid.Text(u"  Orphan.   Q exits."),
            'header')
        log = Log()
        logging.getLogger().addHandler(logging.StreamHandler(log))

        body = urwid.Columns([
            urwid.LineBox(main_widget),
            ('fixed', 30, log),
            ])
        super(MainFrame, self).__init__(
            urwid.AttrWrap(body, 'body'),
            header=header)
