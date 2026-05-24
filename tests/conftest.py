# SPDX-FileCopyrightText: 2023 Graz University of Technology.
# SPDX-License-Identifier: BSD-3-Clause

"""Conftest."""

import pytest
from flask import Flask

from flask_menu import Menu


@pytest.fixture(scope="function")
def app():
    """Doc example app."""
    app = Flask("test")
    Menu(app)
    return app
