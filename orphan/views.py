# -*- coding: utf-8 -*-
"""views.py -- Orphan views.
"""
import logging
logger = logging.getLogger('views')

from collections import defaultdict
import urwid
import urwid.raw_display

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
                entity = at.entity
                terra = at.terrain
                height = at.height
                if entity:
                    text = (palette.as_name(entity.foreground_slug(at)
                                            if callable(entity.foreground_slug)
                                            else entity.foreground_slug,
                    
                                            terra.background_slug(at)
                                            if callable(terra.background_slug)
                                            else terra.background_slug),
                                            
                            entity.glyph(at) if callable(entity.glyph) else entity.glyph
                            )
                else:
                    text = (palette.as_name(terra.foreground_slug(at)
                                            if callable(terra.foreground_slug)
                                            else terra.foreground_slug,
                    
                                            terra.background_slug(at)
                                            if callable(terra.background_slug)
                                            else terra.background_slug),
                                            
                            terra.glyph(at) if callable(terra.glyph) else terra.glyph
                            )
                row_text.append(text)
            rendered_rows.append(
                (Text(row_text).render((columns,)), None, None)
                )
        rendered_rows.pop()
        status_text = '%s Terrain: %s' % (block.phone_book[1].position, terrain[block.terrain[row, col]])
        rendered_rows.append((Text(('important', status_text)).render((columns,)), None, None))
        canvas = urwid.CanvasCombine(rendered_rows)
        return canvas


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
