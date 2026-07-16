# SPDX-FileCopyrightText: 2013-2023 CERN.
# SPDX-FileCopyrightText: 2017 Marlin Forbes.
# SPDX-FileCopyrightText: 2023-2024 Graz University of Technology.
# SPDX-FileCopyrightText: 2026 TU Wien.
# SPDX-License-Identifier: BSD-3-Clause

"""This extension allows creation of menus organised in a tree structure.

Those menus can be then displayed using templates.
"""

from .ext import Menu
from .menu import MenuNode
from .proxies import current_menu

__version__ = "2.0.1"

__all__ = ("current_menu", "Menu", "MenuNode", "__version__")
