# -*- coding: utf-8 -*-
"""orphan.scheduler -- even agents need someone to keep their schedules for them.

Copyright 2011 David Eyk. All rights reserved.
"""
import logging
logger = logging.getLogger('scheduler')
from collections import deque

import owyl


class Scheduler(object):
    def __init__(self):
        self.scheduled = deque()  # A sequence of iterables.
        self.to_schedule = deque()
        self.active = False
        self.kill = False
        self.success = True
        super(Scheduler, self).__init__()

    def __iter__(self):
        self.active = True
        to_remove = set()
        to_schedule = self.to_schedule
        schedule = self.scheduled
        while not self.kill:
            for n, scheduled in enumerate(schedule):
                try:
                    yield scheduled.next()
                except StopIteration:
                    to_remove.add(n)
                except RuntimeError:
                    logger.exception('%s encountered a RuntimeError on %s:', self, scheduled)
                    raise
            
            # Remove any exhausted iterators.
            for n in sorted(to_remove, reverse=True):
                del schedule[n]
            to_remove.clear()

            if to_schedule:
                self._schedule(to_schedule)
                to_schedule.clear()

            # Just in case our schedule ever empties...
            yield None

        yield self.success
        self.active = False
        raise StopIteration()

    def __call__(self):
        return iter(self)

    def _schedule(self, iterables):
        items = [iter(i) for i in iterables]
        self.scheduled.extend(items)
        return self

    def schedule(self, *iterables):
        if self.active:
            self.to_schedule.extend(iterables)
        else:
            self._schedule(iterables)

    def schedule_visit(self, *tasks):
        items = [owyl.visit(t) for t in tasks]
        self.schedule(*items)

    def stop(self):
        self.active = False
        self.kill = True
        return self

    def start(self):
        return self
