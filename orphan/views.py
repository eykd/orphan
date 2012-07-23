# -*- coding: utf-8 -*-
"""views.py -- Orphan views.
"""
import logging
logger = logging.getLogger('views')

from collections import defaultdict
import urwid
import urwid.raw_display
from urwid.util import decompose_tagmarkup

from . import signals
from .entities import entities
from .terrain import terrain

from . import palette


class PlayField(urwid.BoxWidget):
    def __init__(self, block, focus):
        super(PlayField, self).__init__()
        self.block = block
        self.focus = focus
        self.focus = focus

        self.on_block_update = lambda s: self._invalidate()
        signals.block_update.connect(self.on_block_update,
                                     sender=self.block)

    def selectable(self):
        return False

    def render(self, size, focus=False):
        columns, rows = size
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

        # logger.debug('Camera: center c/r (%s, %s), origin c/r (%s, %s)',
        #     center_col, center_row, origin_row, origin_col)

        # Render the camera's view
        block = self.block
        Text = urwid.Text
        rendered_rows = []
        for row in xrange(origin_row, (origin_row + rows)):
            row_text = []
            # Displayed columns are double-wide
            for col in xrange(origin_col, (origin_col + (columns // 2))):
                at = block[row, col]

                if at.entity:
                    row_text.append(at.entity.text(at))
                else:
                    row_text.append(at.terrain.text(at))

            rendered_rows.append(
                (Text(row_text).render((columns,)), None, None)
                )
        return urwid.CanvasCombine(rendered_rows)


class Status(urwid.FlowWidget):
    def __init__(self, block):
        self.block = block

        self.on_block_update = lambda s: self._invalidate()
        signals.block_update.connect(self.on_block_update,
                                     sender=self.block)

        super(Status, self).__init__()

    def selectable(self):
        return False

    def rows(self, size, focus=False):
        return 1

    def render(self, size, focus=False):
        columns, rows = size
        block = self.block
        position = block.phone_book[1].position
        scents = u', '.join(u'%s: %s' % (n, m[position]) for n, m in block.scent_maps.iteritems())
        status_text = u'%s, on %s -- %s' % (position, terrain[block.terrain[position]], scents)
        return urwid.Text(('important', status_text[:columns])).render((columns,))


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

        body = urwid.Pile([
            urwid.Columns([
                urwid.LineBox(main_widget),
                ('fixed', 30, log),
                ]),
            ('fixed', 1, Status(main_widget.block)),
            ])
        super(MainFrame, self).__init__(
            urwid.AttrWrap(body, 'body'),
            header=header)
