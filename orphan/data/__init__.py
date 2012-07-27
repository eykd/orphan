# -*- coding: utf-8 -*-
"""orphan.data -- data files.
"""
import appdirs
from path import path

name = 'Orphan'
author = 'Worlds Enough Studios'

USER_DATA = path(appdirs.user_data_dir(name, author))
SITE_DATA = path(appdirs.site_data_dir(name, author))
CACHE_DATA = path(appdirs.user_cache_dir(name, author))
LOG_DATA = path(appdirs.user_log_dir(name, author))
APP_DATA = path(__file__).abspath().dirname()
