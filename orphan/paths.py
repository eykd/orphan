# -*- coding: utf-8 -*-
"""orphan.paths -- path-finding.

Based on `networkx.astar`:

    Copyright (C) 2004-2011 by
    Aric Hagberg <hagberg@lanl.gov>
    Dan Schult <dschult@colgate.edu>
    Pieter Swart <swart@lanl.gov>
    All rights reserved.
    BSD license.
"""
import logging
logger = logging.getLogger('paths')
from heapq import heappush, heappop

import owyl


neighbor_offsets = (
    (1, 1),
    (1, 0),
    (1, -1),
    (0, 1),
    (0, -1),
    (1, 1),
    (1, 0),
    (1, -1),
    )


@owyl.task
def astar_river_path(path=None, map_array=None, source=None, target=None):
    """Return a list of nodes in a shortest path between source and target
    using the A* ("A-star") algorithm.

    There may be more than one shortest path.  This returns only one.

    Parameters
    ----------
    map_array : numpy.array
       2D heightmap array

    source : node
       Starting node for path

    target : node
       Ending node for path
    """
    logger.debug('Mapping path from %s to %s', source, target)
    rows, cols = map_array.shape
    
    # The default heuristic is h=0 - same as Dijkstra's algorithm
    def heuristic(u, v):
        return 0

    # The queue stores priority, node, cost to reach, and parent.
    # Uses Python heapq to keep in priority order.
    # Add each node's hash to the queue to prevent the underlying heap from
    # attempting to compare the nodes themselves. The hash breaks ties in the
    # priority and is guarenteed unique for all nodes in the graph.
    queue = [(0, hash(source), source, 0, None)]

    # Maps enqueued nodes to distance of discovered paths and the
    # computed heuristics to target. We avoid computing the heuristics
    # more than once and inserting the node into the queue too many times.
    enqueued = {}
    # Maps explored nodes to parent closest to the source.
    explored = {}

    i = 0
    while queue:
        # Pop the smallest item from queue.
        _, __, curnode, dist, parent = heappop(queue)

        if curnode == target:
            path[:] = (curnode,)
            yield True
            logger.debug('Mapped path from %s to %s!', source, target)
            raise StopIteration()
            # node = parent
            # while node is not None:
            #     path.append(node)
            #     node = explored[node]
            # path.reverse()
            # return path

        if curnode in explored:
            continue

        explored[curnode] = parent

        for roff, coff in neighbor_offsets:
            nrow, ncol = neighbor = (curnode[0] + roff, curnode[1] + coff)
            if neighbor in explored \
                   or nrow < 0 or ncol < 0 \
                   or nrow >= rows or ncol >= cols:
                continue

            height = map_array[neighbor]
            ncost = dist + height
            if neighbor in enqueued:
                qcost, h = enqueued[neighbor]
                # if qcost < ncost, a longer path to neighbor remains
                # enqueued. Removing it would need to filter the whole
                # queue, it's better just to leave it there and ignore
                # it when we visit the node a second time.
                if qcost < ncost:
                    continue
            else:
                # Our heuristic: simple manhattan distance
                h = height * (abs(neighbor[0] - target[0]) + abs(neighbor[1] - target[1]))
            enqueued[neighbor] = ncost, h
            heappush(queue, (ncost + h, hash(neighbor), neighbor,
                             ncost, curnode))

        i += 1
        if not i % 10000:
            logger.debug('Still mapping. Latest h was %s', h)
            yield None

    logger.error("Node %s not reachable from %s. Shape was %s", source, target, map_array.shape)
    raise ValueError("Node %s not reachable from %s" % (source, target))
