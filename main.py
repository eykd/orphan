#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main.py -- main entry script.
"""
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

from orphan import controllers
from orphan import scenes


def main():
    director = controllers.Director()
    director.run(scenes.Game())


if '__main__' == __name__:
    main()
