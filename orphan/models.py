# -*- coding: utf-8 -*-
"""models.py -- models for Orphan.
"""
import logging
logger = logging.getLogger('models')
import collections
import numpy
import enum


ENTITIES = enum.Enum(
    'empty',
    'wall',
    'player',
    'adult',
    'child',
    'orphan',
    )


class Layer(object):
    def __init__(self, height, width, dtype):
        self.map = numpy.zeros((height, width), dtype=dtype)


class Block(collections.Mapping):
    def __init__(self, height, width):
        self.shape = (height, width)
        self.occupancy = numpy.random.random_integers(0, 1, (height, width))
        # self.occupancy = numpy.zeros((height, width), dtype=int)
        self.identity = numpy.zeros((height, width), dtype=int)
        self.entities = collections.defaultdict(lambda: None)

    def __iter__(self):
        return iter(self.occupancy)

    def __len__(self):
        return len(self.occupancy)

    def __getitem__(self, (y, x)):
        return self.occupancy[y, x]

    def place(self, entity):
        self.entities[entity.eid] = entity
        pos_x, pos_y = entity.position
        self.occupancy[pos_y, pos_x] = entity.type_index
        self.identity[pos_y, pos_x] = entity.eid

    def remove(self, entity):
        self.entities.pop(entity.eid)
        pos_x, pos_y = entity.position
        self.occupancy[pos_y, pos_x] = ENTITIES.empty.index
        self.identity[pos_y, pos_x] = 0

    def move(self, entity, (pos_y, pos_x)):
        if not self.occupied((pos_y, pos_x)):
            old_y, old_x = entity.position
            self.occupancy[old_y, old_x] = ENTITIES.empty.index
            self.occupancy[pos_y, pos_x] = entity.type_index
            return True
        else:
            return False

    def occupied(self, (y, x)):
        return False
        return self.occupancy[y, x] > 0

    def whoIsAt(self, (y, x)):
        return self.entities[self.identity[y, x]]


class Entity(object):
    type_index = None
    next_id = 1

    def __init__(self, block, (pos_y, pos_x), eid=None):
        super(Entity, self).__init__()
        if self.type_index is None:
            raise NotImplementedError('Entity must define a `type_index`. Subclass and define.')
        if eid is None:
            self.eid = self.next_id
            Entity.next_id += 1
        else:
            self.eid = eid
            Entity.next_id = max(eid, Entity.next_id)

        self.position = [pos_y, pos_x]
        self.block = block
        self.block.place(self)

    def __repr__(self):
        return u'<Entity: %s>' % self

    def __unicode__(self):
        return u'%s %s' % (ENTITIES[self.type_index].key, self.eid)

    def updatePosition(self, (new_y, new_x)):
        pos_y, pos_x = self.position
        if new_y is not None:
            pos_y = new_y
        if new_x is not None:
            pos_x = new_x

        if self.block.move(self, (pos_y, pos_x)):
            self.position[:] = (pos_y, pos_x)
            logger.debug('%s now at y/x %s' % (self, self.position))
            return True
        else:
            return False

    def move_north(self):
        return self.updatePosition((self.position[0] - 1, None))

    def move_south(self):
        return self.updatePosition((self.position[0] + 1, None))

    def move_west(self):
        return self.updatePosition((None, self.position[1] - 1))

    def move_east(self):
        return self.updatePosition((None, self.position[1] + 1))


class Player(Entity):
    type_index = ENTITIES.player.index
