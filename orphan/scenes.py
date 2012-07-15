# -*- coding: utf-8 -*-
"""orphan.scenes -- scenes from a game about The Orphan.
"""
import owyl
from . import models
from . import views
from . import controllers
from . import player


class Game(controllers.Scene):
    def on_enter(self):
        self.block = models.Block(1000, 1000)
        self.addChild(self.block.land_agent)
        self.player = models.Player(self.block, (500, 20))
        self.controls = player.Player(self.player)

        self.field = views.PlayField(self.block, self.player)
        self.main_frame = views.MainFrame(self.field)

        self.schedule_visit(
            owyl.repeatAlways(
                owyl.limit(
                    owyl.wrap(self.block.update),
                    limit_period = 0.1)
                )
            )
