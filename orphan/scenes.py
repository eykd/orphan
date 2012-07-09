# -*- coding: utf-8 -*-
"""orphan.scenes -- scenes from a game about The Orphan.
"""
from . import models
from . import views
from . import controllers
from . import player


class Game(controllers.Scene):
    def on_enter(self):
        self.block = models.Block(1000, 1000)
        self.player = models.Player(self.block, (20, 20))
        self.controls = player.Player(self.player)

        self.field = views.PlayField(self.block, self.player)
        self.main_frame = views.MainFrame(self.field)
