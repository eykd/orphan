#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main.py -- main entry script.
"""
import urwid
import urwid.raw_display
urwid.set_encoding("UTF-8")


class CommandMap(urwid.CommandMap):
    _command_defaults = {
        'up': 'cursor up',
        'down': 'cursor down',
        'left': 'cursor left',
        'right': 'cursor right',
        ' ': 'activate',
        'enter': 'activate',
    }


class PlayField(urwid.BoxWidget):
    def __init__(self, *args, **kwargs):
        super(PlayField, self).__init__(*args, **kwargs)
        self.position_x = 20
        self.position_y = 20
        self._command_map = CommandMap()

    def render(self, size, focus=False):
        maxcol, maxrow = size
        player_line = u' ' * self.position_x
        if len(player_line) > maxcol:
            player_line = player_line[:maxcol - 1]
        return urwid.CanvasCombine(
            [(urwid.Text([player_line, ('player', u'文')]).render((maxcol,))
              if line == self.position_y
              else urwid.Text(u'').render((maxcol,)),
              None, None)
             for line in xrange(maxrow)]
            )

    def keypress(self, size, key):
        cmd = self._command_map[key]
        if cmd is None:
            return key
        elif cmd == 'cursor left':
            self.position_x -= 1
            self._invalidate()
        elif cmd == 'cursor right':
            self.position_x += 1
            self._invalidate()
        elif cmd == 'cursor up':
            self.position_y -= 1
            self._invalidate()
        elif cmd == 'cursor down':
            self.position_y += 1
            self._invalidate()
        return key


def main():
    header = urwid.AttrWrap(
        urwid.Text(u"Welcome to the urwid example! Q exits."),
        'header')
    body = urwid.LineBox(
        urwid.Filler(
            urwid.Text(u"Hello, world! \u2592 (▒)")
        )
    )
    body = urwid.LineBox(PlayField())
    frame = urwid.Frame(urwid.AttrWrap(body, 'body'), header=header)

    palette = [
    # (name, foreground, background, mono, foreground_high, background_high)
        ('player', 'light blue', 'light gray', 'standout'),
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

    screen = urwid.raw_display.Screen()

    def unhandled(key):
        if key in 'qQxX' or key == 'esc':
            raise urwid.ExitMainLoop()

    urwid.MainLoop(frame, palette, screen, unhandled_input=unhandled).run()


if '__main__' == __name__:
    main()
