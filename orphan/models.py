# -*- coding: utf-8 -*-
"""models.py -- models for Orphan.
"""
import logging
logger = logging.getLogger('models')
import collections
import numpy
import random

import rlfl
import owyl

from . import agents
from . import signals

from .entities import entities
from .terrain import terrain
from . import heightmap
from . import river


Position = collections.namedtuple('Position', 'row col')
Occupants = collections.namedtuple('Occupants', 'block position height terrain item entity')


class LandAgent(agents.Agent):
    def __init__(self, block):
        super(LandAgent, self).__init__()
        self.block = block

        self.schedule_visit(
            owyl.sequence(
                heightmap.generate_heightmap(heightmap=block.heightmap),
                owyl.wrap(self.addChild, river.RiverGod(block)),
                )
            )


class Block(collections.Mapping):
    def __init__(self, rows, columns, seed=None):
        super(Block, self).__init__()
        shape = self.shape = (rows, columns)

        self.random = random.Random(seed)

        # RLFL map for storing position flags
        self.map_num = rlfl.create_map(columns, rows)
        self.fill_map(terrain.empty.flags)

        # Heightmap, which our land agent will generate w/ fbm.
        self.heightmap = numpy.zeros(shape, dtype=int)

        # Terrain map for features and structures.
        # self.terrain = numpy.random.random_integers(0, 1, (rows, columns))
        self.terrain = numpy.zeros(shape, dtype=int)
        
        # Loop through every cell and populate it.
        for row in xrange(rows):
            for col in xrange(columns):
                # Set flags
                if self.terrain[row, col] > 0:
                    self.clear_flag((row, col), rlfl.CELL_OPEN)
        
        # Entity map for all mobs.
        self.entities = collections.defaultdict(lambda: 0)

        # Item map.
        self.items = collections.defaultdict(lambda: 0)

        self.phone_book = collections.defaultdict(lambda: None)

        self.land_agent = LandAgent(self)

    def __iter__(self):
        return iter(self.entities)

    def __len__(self):
        return len(self.entities)

    def __getitem__(self, position):
        """Return the various Occupants of the given cell.
        """
        return Occupants(block = self,
                         position = position,
                         height = self.heightmap[position],
                         terrain = terrain[self.terrain[position]],
                         entity = self.entities[position],
                         items = 0
                         )

    def __setitem__(self, position, terraindef):
        """Set the terrain for a given cell.
        """
        tmap = self.terrain
        view = tmap[position]
        view.fill(terraindef.index)
        rows, cols = position

        if terraindef.flags is not None or terraindef.clear_flags is not None:
            rows = list(self.slice_to_xrange(rows, len(tmap)))
            cols = list(self.slice_to_xrange(cols, len(tmap[0])))
            flags = terraindef.flags
            clear = terraindef.clear_flags
            set_flag = self.set_flag
            clear_flag = self.clear_flag

            for row in rows:
                for col in cols:
                    shape = (row, col)
                    if flags is not None:
                        set_flag(shape, flags)
                    if clear is not None:
                        clear_flag(shape, clear)
                
    def slice_to_xrange(self, n, maxn):
        if isinstance(n, slice):
            return xrange(
                0 if n.start is None else int(n.start),
                maxn if n.stop is None else int(n.stop),
                1 if n.step is None else int(n.step)
                )
        else:
            return xrange(n, n+1)

    def fill_map(self, flags):
        return rlfl.fill_map(self.map_num, flags)

    def clear_map(self, flags=None):
        if flags is None:
            return rlfl.clear_map(self.map_num)
        else:
            return rlfl.clear_map(self.map_num, flags)

    def has_flag(self, position, flags):
        return rlfl.has_flag(self.map_num, position, flags)

    def set_flag(self, position, flags):
        return rlfl.set_flag(self.map_num, position, flags)

    def clear_flag(self, position, flags):
        return rlfl.clear_flag(self.map_num, position, flags)

    def get_flags(self, position):
        return rlfl.get_flags(self.map_num, position)

    def update(self):
        # logger.debug('Updating block.')
        signals.block_update.send(self)
        
    def _place(self, entity, position=None):
        if position is None:
            position = entity.position
        self.entities[position] = entity
        self.set_flag(position, rlfl.CELL_OCUP)
        
    def place(self, entity):
        self.phone_book[entity.eid] = entity
        self._place(entity, entity.position)
        self.update()

    def _remove(self, entity):
        pos_col, pos_row = entity.position
        self.entities.pop(entity.position)
        self.clear_flag(entity.position, rlfl.CELL_OCUP)

    def remove(self, entity):
        self.phone_book.pop(entity.eid)
        self._remove(entity)
        self.update()

    def move(self, entity, position):
        if self.passable(position):
            self._remove(entity)
            self._place(entity, position)
            self.update()
            return True
        else:
            return False

    def occupied(self, position):
        return self.has_flag(position, rlfl.CELL_OCUP)

    def passable(self, position):
        # logger.info('P:%s\nF:%s', position, self.get_flags(position))
        return self.has_flag(position, rlfl.CELL_WALK) \
               and not self.has_flag(position, rlfl.CELL_OCUP | rlfl.CELL_PERM)


class Entity(object):
    kind = None
    next_id = 1

    def __init__(self, block, (pos_row, pos_col), eid=None):
        super(Entity, self).__init__()
        if self.kind is None:
            raise NotImplementedError('Entity must define a `kind`. Subclass and define.')
        if eid is None:
            self.eid = self.next_id
            Entity.next_id += 1
        else:
            self.eid = eid
            Entity.next_id = max(eid, Entity.next_id)

        self.position = Position(pos_row, pos_col)
        self.block = block
        self.block.place(self)

    def __repr__(self):
        return u'<Entity: %s>' % self

    def __unicode__(self):
        return u'%s %s' % (self.kind.key, self.eid)

    @property
    def foreground_slug(self):
        return self.kind.foreground_slug

    @property
    def glyph(self):
        return self.kind.glyph

    def updatePosition(self, (new_row, new_col)):
        pos_row, pos_col = self.position
        if new_row is not None:
            pos_row = new_row
        if new_col is not None:
            pos_col = new_col
        new_pos = Position(pos_row, pos_col)

        if self.block.move(self, new_pos):
            self.position = new_pos
            # logger.debug('%s now at row/col %s' % (self, self.position))
            return True
        else:
            return False

    def move_north(self):
        return self.updatePosition((self.position.row - 1, None))

    def move_south(self):
        return self.updatePosition((self.position.row + 1, None))

    def move_west(self):
        return self.updatePosition((None, self.position.col - 1))

    def move_east(self):
        return self.updatePosition((None, self.position.col + 1))


class Player(Entity):
    kind = entities.player
