#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main.py -- main entry script.
"""
import logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)

from orphan import controllers


def main():
    director = controllers.Director()
    director.run()


if '__main__' == __name__:
    main()
