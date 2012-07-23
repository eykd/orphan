#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main.py -- main entry script.
"""
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)
logging.captureWarnings(True)

from . import controllers
from . import scenes


def main():
    director = controllers.Director()
    director.run(scenes.WorldGen())


if '__main__' == __name__:
    main()
