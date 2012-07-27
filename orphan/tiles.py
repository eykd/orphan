# -*- coding: utf-8 -*-
"""orphan.tiles -- non-periodic tile-laying using Wang tiles.
"""
import re
from collections import defaultdict

import configobj

import data

TILES_INI = configobj.ConfigObj(data.APP_DATA / 'tiles.ini')

TILES = {}

separator_cp = re.compile('-+\n', re.MULTILINE)


def load():
    for group, section in TILES_INI.iteritems():
        mapping = dict((v, k) for k, v in section['mapping'].iteritems())
        tiles = [
            _Tile(group, tile.strip(), mapping)
            for tile in separator_cp.split(section['tiles'].strip())
            if tile.strip()
            ]
        north = defaultdict(set)
        south = defaultdict(set)
        west = defaultdict(set)
        east = defaultdict(set)
        for tile in tiles:
            north[tile.north].add(tile)
            south[tile.south].add(tile)
            west[tile.west].add(tile)
            east[tile.east].add(tile)

        TILES[group] = dict(
            tiles = tiles,
            north = north,
            south = south,
            west = west,
            east = east,
            )


class _Tile(object):
    def __init__(self, group, tile, mapping):
        super(_Tile, self).__init__()
        self.group = group
        self.tile = tile
        self.mapping = mapping

        m = self.map = []
        a = 0
        # Parse the tile into a list of lists of descriptive strings,
        # using the provided mapping.
        for row in tile.splitlines():
            row = row.strip()
            parcels = []
            for b in xrange(0, len(row)+2, 2):
                parcel = row[a:b]
                if parcel:
                    parcels.append(mapping[parcel])
                a = b
            m.append(parcels)

        self.north = tuple(self.map[0])
        self.south = tuple(self.map[-1])
        self.west = tuple(row[0] for row in self.map)
        self.east = tuple(row[-1] for row in self.map)

    def __unicode__(self):
        return unicode(self.tile)

    def __str__(self):
        return str(self.tile)

    def __repr__(self):
        return u'<Tile:\n%s\n >' % self

    def __hash__(self):
        return hash(self.tile)

    direction_opposites = dict(
        north = 'south',
        south = 'north',
        east = 'west',
        west = 'east',
        )

    def match(self, direction):
        return TILES[self.group][self.direction_opposites[direction]][getattr(self, direction)]
