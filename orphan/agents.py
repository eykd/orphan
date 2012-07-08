# -*- coding: utf-8 -*-
"""orphan.agents -- men of mystery, in (hierarchical) international intrigues. Really, just hierarchical schedulers.

Copyright 2011 David Eyk. All rights reserved.
"""
from collections import deque, defaultdict
import uuid

import blinker

from . import scheduler
from . import switchboard

import owyl


class Agent(scheduler.Scheduler):
    default_drops = {
        'inbox': "This is where we expect to receive messages.",
        }

    default_assignments = {
        'default': "The default work queue."
        }

    switchboard = switchboard.Switchboard()

    def __init__(self, *children, **kwargs):
        super(Agent, self).__init__()
        self.name = kwargs.get('name', uuid.uuid1().hex)
        self.signal = blinker.signal(self.name)
        self.switchboard[self.name] = self.signal
        self.parent = kwargs.get('parent', None)
        self.addChild(*children)

        self.drops = defaultdict(deque)  # For FIFO messages
        for boxname in self.default_drops:
            self.drops[boxname]

        self.assignments = defaultdict(deque)
        for qname in self.default_assignments:
            # Schedule a task queue to handle assignments.
            self.schedule(
                owyl.visit(
                    owyl.queue(
                        self.assignments[qname])))

        self.listeners = defaultdict(deque)
        self.listen(self.name, 'inbox')

    def assign(self, task, queue='default'):
        self.asignments[queue].appendleft(task)

    def listen(self, signal, box):
        def receiver(message):
            self.send(message, box)
        self.listeners[signal].append(receiver)
        self.signal.connect(receiver)
        return self

    def dispatch(self, signal, message):
        signal.send(message)

    def send(self, message, box):
        self.drops[box].appendleft(message)
        return self

    def receive(self, box):
        return self.drops[box].pop()

    def check(self, box):
        return len(self.drops[box])

    def addChild(self, *children):
        for child in children:
            child.parent = self
        self.schedule(*children)
        return self
