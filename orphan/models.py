# -*- coding: utf-8 -*-
"""models.py -- models for Orphan.
"""
import logging
logger = logging.getLogger('models')
import collections
import random

import numpy
import rlfl
import owyl

from . import agents
from . import signals
from . import palette

from .entities import entities
from .terrain import terrain
# from . import heightmap
from . import river


Position = collections.namedtuple('Position', 'row col')
Occupants = collections.namedtuple('Occupants', 'block position terrain items entity')


class LandAgent(agents.Agent):
    def __init__(self, block):
        super(LandAgent, self).__init__()
        self.block = block
        self.addChild(river.RiverGod(block))
        self.schedule_visit(
            owyl.repeatAlways(
                owyl.limit(
                    self.update_scent_values(),
                    limit_period = 0.1
                    )
                )
            )

    @owyl.taskmethod
    def update_scent_values(self, **kwargs):
        scent_maps = self.block.scent_maps
        for name, scents in self.block.scents.iteritems():
            for position, value in scents:
                scent_maps[name][position] = value

            yield None

        yield True
        

class ScentLayer(agents.Agent):
    def __init__(self, name, shape, scale):
        super(ScentLayer, self).__init__()
        self.name = name
        self.map = numpy.zeros(shape, dtype=numpy.float16)
        self.scale = numpy.float16(scale)
        rows, cols = shape
        dx = self.dx = 1.0 / cols
        dy = self.dy = 1.0 / rows
        dx2 = self.dx2 = dx ** 2
        dy2 = self.dy2 = dy ** 2
        dt = self.dt = dx2 *dy2 / (2 * scale * (dx2 + dy2))

        # Save these for later use in the diffusion equation...
        self.tscale = dt * scale
        self._1_dx2 = 1.0 / dx2
        self._1_dy2 = 1.0 / dy2
        
        self.buffer = numpy.zeros(shape, dtype=numpy.float16)
        self.schedule_visit(
            owyl.repeatAlways(
                owyl.limit(
                    self.update_scents(),
                    limit_period = 0.1
                    )
                )
            )

    def __getitem__(self, key):
        return self.map[key]

    def __setitem__(self, key, value):
        self.map[key] = value

    @owyl.taskmethod
    def update_scents(self, **kwargs):
        """Update the scent layer.
        """
        buf = self.buffer
        cur = self.map

        # MAGIC: Lickety-split C math! I don't know how this works, but I like it!
        # http://www.timteatro.net/2010/10/29/performance-python-solving-the-2d-diffusion-equation-with-numpy/
        buf[1:-1, 1:-1] = cur[1:-1, 1:-1] + self.tscale*(
            (cur[2:, 1:-1] - 2*cur[1:-1, 1:-1] + cur[:-2, 1:-1]) * self._1_dx2 +
            (cur[1:-1, 2:] - 2*cur[1:-1, 1:-1] + cur[1:-1, :-2]) * self._1_dy2
            ) 

        # Swap the map and the buffer
        self.map, self.buffer = self.buffer, self.map

        yield True


class Block(collections.Mapping):
    def __init__(self, rows, columns, seed=None):
        super(Block, self).__init__()
        shape = self.shape = (rows, columns)

        self.scent_maps = {}
        self.scents = collections.defaultdict(collections.deque)
        self.random = random.Random(seed)

        # RLFL map for storing position flags
        self.map_num = rlfl.create_map(columns, rows)

        # Terrain map for features and structures.
        # self.terrain = numpy.random.random_integers(0, 1, (rows, columns))
        self.terrain = numpy.zeros(shape, dtype=int)

        self[:, :] = terrain.dirt
        
        # Entity map for all mobs.
        self.entities = collections.defaultdict(lambda: 0)

        # Item map.
        self.items = collections.defaultdict(lambda: 0)

        self.phone_book = collections.defaultdict(lambda: None)

        self.land_agent = LandAgent(self)

        self.addScentLayer('water', 0.95)

    def __iter__(self):
        return iter(self.entities)

    def __len__(self):
        return len(self.entities)

    def __getitem__(self, position):
        """Return the various Occupants of the given cell.
        """
        return Occupants(block = self,
                         position = position,
                         terrain = terrain[self.terrain[position]],
                         entity = self.entities[position],
                         items = 0
                         )

    def __setitem__(self, position, terraindef):
        """Set the terrain for a given cell.
        """
        tmap = self.terrain
        tmap[position].fill(terraindef.index)
        rows, cols = position

        # Set up scents
        scents = self.scents
        for name, value in terraindef.scents:
            scents[name].append((position, value))

        # Set terrain flags.
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

    def addScentLayer(self, name, scale=0.5):
        layer = self.scent_maps[name] = ScentLayer(name, self.shape, scale)
        self.land_agent.addChild(layer)
        return layer

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

    def text(self, at):
        terra = at.terrain
        return (palette.as_name(self.foreground_slug(at)
                                if callable(self.foreground_slug)
                                else self.foreground_slug,

                                terra.background_slug(at)
                                if callable(terra.background_slug)
                                else terra.background_slug),

                self.glyph(at) if callable(self.glyph) else self.glyph
                )

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
