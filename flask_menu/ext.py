# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2013, 2014, 2015, 2017 CERN
# Copyright (C) 2017 Marlin Forbes
# Copyright (C) 2023 Graz University of Technology.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Ext."""

from flask import current_app, g

from .menu import MenuRoot


class Menu:
    """Flask extension implementation."""

    def __init__(self, app=None):
        """Initialize Menu extension."""
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize a Flask application."""
        self.app = app
        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, "extensions"):
            app.extensions = {}
        if "menu" in app.extensions:
            raise RuntimeError("Flask application is already initialized.")
        app.extensions["menu"] = MenuRoot("", None)

        app.context_processor(lambda: {"current_menu": Menu.root()})

        @app.url_value_preprocessor
        def url_preprocessor(route, args):
            """Store the current route endpoint and arguments."""
            g._menu_kwargs = args
            g._menu_route = route

    @staticmethod
    def root():
        """Return a root entry of current application's menu."""
        return current_app.extensions["menu"]
