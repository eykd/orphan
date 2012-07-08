# -*- coding: utf-8 -*-
"""orphan.scheduler -- even agents need someone to keep their schedules for them.

Copyright 2011 David Eyk. All rights reserved.
"""
from collections import deque


class Scheduler(object):
    def __init__(self):
        self.scheduled = deque()  # A sequence of iterables.
        self.active = False
        self.kill = False
        super(Scheduler, self).__init__()

    def __iter__(self):
        to_remove = set()
        schedule = self.scheduled
        while not self.kill:
            for n, scheduled in enumerate(schedule):
                try:
                    yield scheduled.next()
                except StopIteration:
                    to_remove.add(n)
            
            # Remove any exhausted iterators.
            for n in sorted(to_remove, reverse=True):
                del schedule[n]
            to_remove.clear()
        
        raise StopIteration()

    def __call__(self):
        self.active = True
        return iter(self)

    def schedule(self, *iterables):
        self.scheduled.extend(iter(i) for i in iterables)
        return self

    def stop(self):
        self.active = False
        self.kill = True
        return self

    def start(self):
        return self
