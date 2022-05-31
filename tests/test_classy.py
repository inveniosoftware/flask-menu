# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2013, 2014, 2015 CERN.
# Copyright (C) 2017 Marlin Forbes
# Copyright (C) 2022 Graz University of Technology.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Test Classy."""

from flask import Blueprint
from flask_classy import FlaskView, route

from flask_menu import current_menu
from flask_menu.classy import classy_menu_item, register_flaskview


def test_classy_endpoint_on_blueprint(app):
    class MyEndpoint(FlaskView):
        route_base = "/"

        def index(self):
            return ""

        @classy_menu_item("page1", "Page 1")
        def page1(self):
            return ""

        @classy_menu_item("page2", "Page 2")
        def page2(self):
            return ""

        @classy_menu_item("page3", "Page 3")
        @classy_menu_item("page31", "Page 3.1")
        def page3(self):
            return ""

    bp = Blueprint("foo", "foo", url_prefix="/foo")

    MyEndpoint.register(bp)
    register_flaskview(bp, MyEndpoint)

    app.register_blueprint(bp)

    data = {
        "/foo/page1/": {
            "page1": True,
            "page2": False,
            "page3": False,
            "page31": False,
        },
        "/foo/page2/": {
            "page1": False,
            "page2": True,
            "page3": False,
            "page31": False,
        },
        "/foo/page3/": {
            "page1": False,
            "page2": False,
            "page3": True,
            "page31": True,
        },
    }

    def assert_msg(active_is):
        path_msg = f"path={path}"
        submenu_msg = "submenu_by_endpoint={endpoint}"
        is_msg = "active_is={active_is}"
        should_msg = "active_should={active_should}"
        return f"{path_msg} {submenu_msg} {is_msg} {should_msg}"

    for (path, v) in data.items():
        with app.test_client() as c:
            c.get(path)
            for (endpoint, active_should) in v.items():
                active_is = current_menu.submenu(endpoint).active
                assert active_is == active_should, assert_msg(active_is)


def test_classy_endpoint_with_args(app):
    class MyEndpoint(FlaskView):
        route_base = "/"

        @classy_menu_item("withid.page1", "Page 1")
        @route("/<int:id>/page1")
        def page1(self, id):
            return "page1"

        @classy_menu_item("withid.page2", "Page 2")
        @route("/<int:id>/page2")
        def page2(self, id):
            return "page2"

    MyEndpoint.register(app)
    register_flaskview(app, MyEndpoint)

    data = {
        "/1/page1": {
            "withid.page1": True,
            "withid.page2": False,
        },
        "/1/page2": {
            "withid.page1": False,
            "withid.page2": True,
        },
    }

    def assert_msg(active_is):
        path_msg = f"path={path}"
        submenu_msg = "submenu_by_endpoint={endpoint}"
        is_msg = "active_is={active_is}"
        should_msg = "active_should={active_should}"
        return f"{path_msg} {submenu_msg} {is_msg} {should_msg}"

    for (path, v) in data.items():
        with app.test_client() as c:
            c.get(path)
            for (endpoint, active_should) in v.items():
                active_is = current_menu.submenu(endpoint).active
                assert active_is == active_should, assert_msg(active_is)


def test_classy_endpoint(app):
    class MyEndpoint(FlaskView):
        route_base = "/"

        def index(self):
            return ""

        @classy_menu_item("page1", "Page 1")
        def page1(self):
            return ""

        @classy_menu_item("page2", "Page 2")
        def page2(self):
            return ""

        @classy_menu_item("page3", "Page 3")
        @classy_menu_item("page31", "Page 3.1")
        def page3(self):
            return ""

    MyEndpoint.register(app)
    register_flaskview(app, MyEndpoint)

    data = {
        "/page1/": {"page1": True, "page2": False, "page3": False, "page31": False},
        "/page2/": {"page1": False, "page2": True, "page3": False, "page31": False},
        "/page3/": {"page1": False, "page2": False, "page3": True, "page31": True},
    }

    def assert_msg(active_is):
        path_msg = f"path={path}"
        submenu_msg = "submenu_by_endpoint={endpoint}"
        is_msg = "active_is={active_is}"
        should_msg = "active_should={active_should}"
        return f"{path_msg} {submenu_msg} {is_msg} {should_msg}"

    for (path, v) in data.items():
        with app.test_client() as c:
            c.get(path)
            for (endpoint, active_should) in v.items():
                active_is = current_menu.submenu(endpoint).active
                assert active_is == active_should, assert_msg(active_is)
