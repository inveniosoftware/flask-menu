# SPDX-FileCopyrightText: 2013, 2014, 2015, 2017 CERN
# SPDX-FileCopyrightText: 2017 Marlin Forbes
# SPDX-FileCopyrightText: 2023 Graz University of Technology.
# SPDX-License-Identifier: BSD-3-Clause

"""Proxies."""

from werkzeug.local import LocalProxy

from .ext import Menu

#: Global object that is proxy to the current application menu.
current_menu = LocalProxy(Menu.root)
