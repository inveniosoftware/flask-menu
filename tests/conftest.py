# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2022 Graz University of Technology.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Conftest."""

import pytest
from flask import Flask

from flask_menu import FlaskMenu


@pytest.fixture(scope="function")
# def app(resource):
def app():
    """Doc example app."""
    print("fixture app")
    app = Flask("test")
    FlaskMenu(app)
    # app.register_blueprint(resource.as_blueprint())
    return app
