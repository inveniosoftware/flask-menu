# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2013, 2014, 2015, 2017 CERN
# Copyright (C) 2017 Marlin Forbes
# Copyright (C) 2022 Graz University of Technology.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""This extension allows creation of menus organised in a tree structure.

Those menus can be then displayed using templates.
"""

from .decorator import register_menu
from .ext import FlaskMenu
from .ext import FlaskMenu as Menu
from .proxies import current_menu

__version__ = "0.7.2"

__all__ = ("current_menu", "register_menu", "FlaskMenu", "Menu", "__version__")
