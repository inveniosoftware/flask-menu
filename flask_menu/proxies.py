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

"""Flask Menu."""

from werkzeug.local import LocalProxy

from .ext import FlaskMenu

#: Global object that is proxy to the current application menu.
current_menu = LocalProxy(FlaskMenu.root)
