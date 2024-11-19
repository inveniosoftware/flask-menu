# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2013-2023 CERN
# Copyright (C) 2017 Marlin Forbes
# Copyright (C) 2023-2024 Graz University of Technology.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""This extension allows creation of menus organised in a tree structure.

Those menus can be then displayed using templates.
"""

from .ext import Menu
from .menu import MenuNode
from .proxies import current_menu

__version__ = "2.0.0"

__all__ = ("current_menu", "Menu", "MenuNode", "__version__")
