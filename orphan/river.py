# -*- coding: utf-8 -*-
"""orphan.river -- the river god
"""
import logging
logger = logging.getLogger('river')
from collections import deque

import numpy
from noise import pnoise1
import networkx as nx
import owyl

from . import agents
from . import paths
from . import terrain


class RiverGod(agents.Agent):
    def __init__(self, block):
        super(RiverGod, self).__init__()
        logger.debug('Initializing RiverGod...')
        self.block = block
        rows, columns = block.shape
        # Constrain the river source and end to the middle third
        rows_1_3 = rows // 3
        rows_2_3 = (rows * 2) // 3
        start_row = self.start_row = self.block.random.randint(rows_1_3, rows_2_3)
        end_row = self.end_row = self.block.random.randint(rows_1_3, rows_2_3)
        self.path = []
        self.schedule_visit(
            owyl.sequence(
                self.draw_river(
                    start = (start_row, 0),
                    end = (end_row, columns - 1),
                    scale = 50
                    ),
                owyl.wrap(self.stop)
                )
            )

    @owyl.taskmethod
    def draw_river(self, start=(0, 0), end=(0, 0), scale=1):
        """Draw a river on the terrain map.

        Uses a midpoint-displacement algorithm for the course and 1D
        perlin noise for the width.
        """
        logger.debug('Drawing the river from %s to %s...', start, end)
        rand = self.block.random.random
        queue = deque([(start, end, scale)])
        cols = set()

        base = self.block.random.randint(0, 1000)
        max_row, max_col = self.block.shape
        water = terrain.water
        terrain_array = self.block.terrain

        i = 0
        while queue:
            (a_row, a_col), (b_row, b_col), scale = queue.pop()
            self.draw(a_row, a_col, base, water)
            self.draw(b_row, b_col, base, water)
            cols.add(a_col)
            cols.add(b_col)

            # Calculate midpoint displacement.
            m_row = int((a_row + b_row) * 0.5)
            m_col = int((a_col + b_col) * 0.5)
            if m_col in cols:
                continue
            amount = rand()
            amount *= scale
            scale *= 0.5
            m_row += amount
            queue.appendleft(((m_row, m_col), (b_row, b_col), scale))
            queue.appendleft(((a_row, a_col), (m_row, m_col), scale))

            i += 1
            if not i % 100:
                if not i % 1000:
                    'Still drawing...'
                yield None

        self.block.update()
        logger.debug('Drew river!')
        yield True

    def draw(self, row, col, noise_base, fill):
        mod_up = int(round(5 * pnoise1(col * 0.01, base=noise_base)))
        mod_down = int(round(5 * pnoise1(col * 0.01, base=-noise_base)))
        width_2 = 20
        top_row = row - (width_2 + mod_up)
        bot_row = row + (width_2 + mod_down)
        try:
            self.block[top_row : bot_row + 1, col : col + 1] = fill
        except IndexError:
            logger.exception('Bad terrain index (shape %s): %s : %s, %s : %s', self.block.terrain.shape, top_row, bot_row, col, col)
            raise
