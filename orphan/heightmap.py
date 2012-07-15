# -*- coding: utf-8 -*-
"""orphan.heightmap -- heightmap generation.
"""
import logging
logger = logging.getLogger('heightmap')
import noise
import owyl


@owyl.task
def generate_heightmap(heightmap=None, offset=(0, 0)):
    logger.debug('Generating heightmap...')
    if heightmap is None:
        raise ValueError('`heightmap` must be an array.')
    rows, columns = heightmap.shape
    off_rows, off_cols = offset

    pnoise2 = noise.snoise2
    min_fbm = 100000
    max_fbm = 0
    min_h = 10000
    max_h = 0
    i = 0
    for row in xrange(rows):
        for col in xrange(columns):
            fbm = pnoise2((row + off_rows) * 0.01, (col + off_cols) * 0.01, 3)
            min_fbm = min(fbm, min_fbm)
            max_fbm = max(fbm, max_fbm) 
            h = int((fbm + 1) * 25)  # Ranges roughly from 1.0 to 50.0.
            min_h = min(h, min_h)
            max_h = max(h, max_h)
            heightmap[row, col] = h
            i += 1
            if not i % 10000:
                yield None

    logger.debug('Generated heightmap!')
    yield True
