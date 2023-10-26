# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2013, 2014, 2015 CERN.
# Copyright (C) 2017 Marlin Forbes
# Copyright (C) 2023 Graz University of Technology.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Test Core."""

from flask import Blueprint, request, url_for
from pytest import raises

from flask_menu import Menu, current_menu, register_menu


def test_simple_app_menu(app):
    """Test simple app."""
    menu = app.extensions["menu"].root()

    menu.submenu(".").register("test", "Test")
    menu.submenu(".level2").register("level2", "Level 2")
    menu.submenu(".level2.level3").register("level3", "Level 3")
    menu.submenu(".level2.level3B").register("level3B", "Level 3B", order=1)

    @app.route("/test")
    def test():
        return "test"

    @app.route("/level2")
    def level2():
        return "level2"

    @app.route("/level3")
    def level3():
        return "level3"

    @app.route("/level3B")
    def level3B():
        return "level3B"

    with app.test_client() as c:
        c.get("/test")
        assert request.endpoint == "test"
        assert current_menu.url == "/test"
        assert current_menu.text == "Test"
        assert current_menu.active
        assert current_menu.submenu("level2").text == "Level 2"
        assert not current_menu.submenu("level2").active
        assert current_menu.submenu("missing", auto_create=False) is None
        assert len(current_menu.list_path(".", ".level2.level3")) == 3
        assert current_menu.list_path(".", "missing") is None
        assert current_menu.list_path("missing", ".level2.level3") is None
        assert current_menu.list_path("level2.level3B", "level2.level3") is None

    with app.test_client() as c:
        c.get("/level2")
        assert current_menu.submenu("level2").active

    with app.test_client() as c:
        c.get("/level3")
        assert current_menu.submenu(".level2.level3").active
        assert current_menu.submenu("level2.level3").active

        assert not current_menu.has_active_child(recursive=False)
        assert current_menu.has_active_child()
        assert current_menu.submenu("level2").has_active_child(recursive=False)
        assert current_menu.submenu("level2").has_active_child()

        item_1 = current_menu.submenu("level2.level3")
        item_2 = current_menu.submenu("level2.level3B")
        assert item_1.order < item_2.order
        assert item_1 == current_menu.submenu("level2").children[0]
        assert item_2 == current_menu.submenu("level2").children[1]


def test_simple_app_register_menu(app):
    """Test simple app."""

    @app.route("/test")
    @register_menu(app, ".", "Test")
    def test():
        return "test"

    @app.route("/level2")
    @register_menu(app, "level2", "Level 2")
    def level2():
        return "level2"

    @app.route("/level3")
    @register_menu(app, "level2.level3", "Level 3")
    def level3():
        return "level3"

    @app.route("/level3B")
    @register_menu(app, "level2.level3B", "Level 3B", order=1)
    def level3B():
        return "level3B"

    with app.test_client() as c:
        c.get("/test")
        assert request.endpoint == "test"
        assert current_menu.url == "/test"
        assert current_menu.text == "Test"
        assert current_menu.active
        assert current_menu.submenu("level2").text == "Level 2"
        assert not current_menu.submenu("level2").active
        assert current_menu.submenu("missing", auto_create=False) is None
        assert len(current_menu.list_path(".", ".level2.level3")) == 3
        assert current_menu.list_path(".", "missing") is None
        assert current_menu.list_path("missing", ".level2.level3") is None
        assert current_menu.list_path("level2.level3B", "level2.level3") is None

    with app.test_client() as c:
        c.get("/level2")
        assert current_menu.submenu("level2").active

    with app.test_client() as c:
        c.get("/level3")
        assert current_menu.submenu(".level2.level3").active
        assert current_menu.submenu("level2.level3").active

        assert not current_menu.has_active_child(recursive=False)
        assert current_menu.has_active_child()
        assert current_menu.submenu("level2").has_active_child(recursive=False)
        assert current_menu.submenu("level2").has_active_child()

        item_1 = current_menu.submenu("level2.level3")
        item_2 = current_menu.submenu("level2.level3B")
        assert item_1.order < item_2.order
        assert item_1 == current_menu.submenu("level2").children[0]
        assert item_2 == current_menu.submenu("level2").children[1]


def test_blueprint_menu(app):
    """Test Blueprint."""
    blueprint = Blueprint("foo", "foo", url_prefix="/foo")

    menu = app.extensions["menu"].root()

    menu.submenu(".").register("foo.test", "Test")
    menu.submenu("bar").register("foo.bar", "Foo Bar")

    @app.route("/test")
    def test():
        return "test"

    @blueprint.route("/bar")
    def bar():
        return "bar"

    app.register_blueprint(blueprint)

    with app.test_client() as c:
        c.get("/test")
        assert request.endpoint == "test"
        assert current_menu.text == "Test"

    with app.test_client() as c:
        c.get("/foo/bar")
        assert current_menu.submenu("bar").text == "Foo Bar"
        assert current_menu.submenu("bar").active


def test_blueprint_register_menu(app):
    """Test Blueprint."""
    blueprint = Blueprint("foo", "foo", url_prefix="/foo")

    @app.route("/test")
    @register_menu(blueprint, ".", "Test")
    def test():
        return "test"

    @blueprint.route("/bar")
    @register_menu(blueprint, "bar", "Foo Bar")
    def bar():
        return "bar"

    app.register_blueprint(blueprint)

    with app.test_client() as c:
        c.get("/test")
        assert request.endpoint == "test"
        assert current_menu.text == "Test"

    with app.test_client() as c:
        c.get("/foo/bar")
        assert current_menu.submenu("bar").text == "Foo Bar"
        assert current_menu.submenu("bar").active


def test_visible_when(app):
    """Test visible when."""

    @app.route("/always")
    @register_menu(app, "always", "Always", visible_when=lambda: True)
    def always():
        return "never"

    @app.route("/never")
    @register_menu(app, "never", "Never", visible_when=lambda: False)
    def never():
        return "never"

    @app.route("/normal")
    @register_menu(app, "normal", "Normal")
    def normal():
        return "normal"

    data = {
        "never": {"never": False, "always": True, "normal": True},
        "always": {"never": False, "always": True, "normal": True},
        "normal": {"never": False, "always": True, "normal": True},
    }
    for k, v in data.items():
        with app.test_client() as c:
            c.get("/" + k)
            for endpoint, visible in v.items():
                assert current_menu.submenu(endpoint).visible == visible

    with app.test_request_context():
        current_menu.submenu("always").hide()

    data = {
        "never": {"never": False, "always": False, "normal": True},
        "always": {"never": False, "always": False, "normal": True},
        "normal": {"never": False, "always": False, "normal": True},
    }
    for k, v in data.items():
        with app.test_client() as c:
            c.get("/" + k)
            for endpoint, visible in v.items():
                assert current_menu.submenu(endpoint).visible == visible


def test_visible_when_with_dynamic(app):
    """Test visible when with dynamic."""

    @app.route("/always")
    @register_menu(app, "always", "Always", visible_when=lambda: True)
    def always():
        return "never"

    @app.route("/never")
    @register_menu(app, "never", "Never", visible_when=lambda: False)
    def never():
        return "never"

    @app.route("/normal/<int:id>/")
    @register_menu(app, "normal", "Normal")
    def normal(id):
        return "normal"

    data = {
        "never": {"never": False, "always": True, "normal": True},
        "always": {"never": False, "always": True, "normal": True},
        "normal": {"never": False, "always": True, "normal": True},
    }
    for k, v in data.items():
        with app.test_client() as c:
            c.get("/" + k)
            for endpoint, visible in v.items():
                assert current_menu.submenu(endpoint).visible == visible

    with app.test_request_context():
        current_menu.submenu("always").hide()

    data = {
        "never": {"never": False, "always": False, "normal": True},
        "always": {"never": False, "always": False, "normal": True},
        "normal": {"never": False, "always": False, "normal": True},
    }
    for k, v in data.items():
        with app.test_client() as c:
            c.get("/" + k)
            for endpoint, visible in v.items():
                assert current_menu.submenu(endpoint).visible == visible


def test_active_item(app):
    """Test active_item method."""

    @app.route("/")
    @register_menu(app, "root", "root")
    def root():
        return "root"

    @app.route("/sub1/item1")
    @register_menu(app, "root.sub1.item1", "Sub 1 - Item 1")
    def sub1_item1():
        return "sub1_item1"

    @app.route("/sub2/item1")
    @register_menu(app, "root.sub2.item1", "Sub 2 - Item 1")
    def sub2_item1():
        return "sub2_item1"

    @app.route("/sub2/item2")
    @register_menu(app, "root.sub2.item2", "Sub 2 - Item 2")
    def sub2_item2():
        return "sub2_item2"

    with app.test_client() as c:
        c.get("/")
        assert current_menu.active_item == current_menu.submenu("root")
        c.get("/sub1/item1")
        assert current_menu.active_item == current_menu.submenu("root.sub1.item1")
        sub1 = current_menu.submenu("root.sub1")
        assert sub1.active_item == current_menu.submenu("root.sub1.item1")
        sub2 = current_menu.submenu("root.sub2")
        assert sub2.active_item is None
        c.get("/sub2/item2")
        assert sub2.active_item == current_menu.submenu("root.sub2.item2")


def test_active_when(app):
    """Test active when."""

    @app.route("/")
    @register_menu(app, "root", "Root")
    def root():
        return "root"

    @app.route("/always")
    @register_menu(app, "always", "Always", active_when=lambda: True)
    def always():
        return "always"

    @app.route("/never")
    @register_menu(app, "never", "Never", active_when=lambda: False)
    def never():
        return "never"

    @app.route("/normal")
    @app.route("/normal/<path:path>")
    @register_menu(
        app,
        "normal",
        "Normal",
        active_when=lambda self: request.endpoint == self._endpoint,
    )
    def normal(path=None):
        return "normal"

    data = {
        "/never": {"root": False, "never": False, "always": True, "normal": False},
        "/always": {"root": False, "never": False, "always": True, "normal": False},
        "/normal": {"root": False, "never": False, "always": True, "normal": True},
        "/normal/foo": {
            "root": False,
            "never": False,
            "always": True,
            "normal": True,
        },
        "/bar/normal": {
            "root": False,
            "never": False,
            "always": True,
            "normal": False,
        },
        "/bar/normal/foo": {
            "root": False,
            "never": False,
            "always": True,
            "normal": False,
        },
        "/": {"root": True, "never": False, "always": True, "normal": False},
        "": {"root": True, "never": False, "always": True, "normal": False},
    }

    def assert_msg(active_is):
        path_msg = f"path={path}"
        submenu_msg = f"submenu_by_endpoint={endpoint}"
        is_msg = f"active_is={active_is}"
        should_msg = f"active_should={active_should}"
        return f"{path_msg} {submenu_msg} {is_msg} {should_msg}"

    for path, testset in data.items():
        with app.test_client() as c:
            c.get(path)
            for endpoint, active_should in testset.items():
                active_is = current_menu.submenu(endpoint).active
                assert active_is == active_should, assert_msg(active_is)


def test_dynamic_url(app):
    """Test dynamic url."""

    @app.route("/<int:id>/<string:name>")
    @register_menu(
        app,
        "test",
        "Test",
        endpoint_arguments_constructor=lambda: {
            "id": request.view_args["id"],
            "name": request.view_args["name"],
        },
    )
    def test(id, name):
        return str(id) + ":" + name

    with app.test_request_context():
        url = url_for("test", id=1, name="foo")

    with app.test_client() as c:
        c.get(url)
        assert url == current_menu.submenu("test").url
        assert current_menu.submenu("missing").url == "#"


def test_kwargs(app):
    """Test optional arguments."""
    count = 5

    @app.route("/test")
    @register_menu(app, "test", "Test", count=count)
    def test():
        return "count"

    with app.test_client() as c:
        c.get("/test")
        assert count == current_menu.submenu("test").count


def test_kwargs_override(app):
    """Test if optional arguments cannot be overriden with different value."""

    @app.route("/test")
    def test():
        return "view test"

    with raises(RuntimeError):
        current_menu.submenu("test").register("test", "Test", url="/test1")


def test_external_url(app):
    """Test that external_url works, and is not overriding endpoint."""
    url = "https://python.org"

    item1 = current_menu.submenu("menuitem1")

    # Do not allow endpoint and external_url at the same time.
    with raises(TypeError):
        item1.register(endpoint="test", text="Test", external_url=url)

    item1.register(text="Test", external_url=url)
    assert current_menu.submenu("menuitem1").url == url


def test_double_instantiation(app):
    """Test double Instantiation."""
    with raises(RuntimeError):
        Menu(app)


def test_dynamic_url_with_auto_args(app):
    """Ensure url can be generated by inferring args from current route."""


def test_dynamic_blueprint_with_auto_args(app):
    """Test dynamic blueprint with auto args."""


def test_dynamic_list_constructor(app):
    """Test dynamic list constructor."""

    bar = ["Item 1", "Item 2", "Item 3"]

    def get_menu_items():
        return bar

    @app.route("/")
    @register_menu(app, "foo", "foo", dynamic_list_constructor=get_menu_items)
    def foo():
        return "foo"

    @app.route("/other")
    @register_menu(app, "other", "Other")
    def other():
        return "other"

    with app.test_client() as c:
        c.get("/")
        assert current_menu.submenu("foo").dynamic_list == bar
        assert current_menu.submenu("other").dynamic_list == [
            current_menu.submenu("other")
        ]


# NOTE: this test is with the new structure not that easy.
def test_app_without_existing_extensions(app):
    del app.extensions
    Menu(app)
    assert len(app.extensions) == 1


def test_has_visible_child(app):
    """Test has visible child."""

    @app.route("/one")
    def one():
        return "one"

    # This item should never be visible.
    @app.route("/one/four")
    @register_menu(app, "one.four", "One Four", visible_when=lambda: False)
    def one_four():
        return "one_four"

    @app.route("/six")
    def six():
        return "six"

    # This item should never be visible.
    @app.route("/six/seven")
    @register_menu(app, "six.seven", "Six Seven", visible_when=lambda: False)
    def six_seven():
        return "six_seven"

    @app.route("/six/seven/eight")
    @register_menu(app, "six.seven.eight", "Six Seven Eight")
    def six_seven_eight():
        return "six_seven_eight"

    @app.route("/two")
    @register_menu(app, "two", "Trow")
    def two():
        return "two"

    @app.route("/two/three")
    @register_menu(app, "two.three", "Two Three")
    def two_three():
        return "two_three"

    @app.route("/two/three/five")
    @register_menu(app, "two.three.five", "Two Three Five")
    def two_three_five():
        return "two_three_five"

    data = {
        "/one": {
            "one": False,
            "two": True,
            "two.three": True,
            "one.four": False,
            "two.three.five": False,
            "six": True,
            "six.seven": True,
            "six.seven.eight": False,
        },
        "/two": {
            "one": False,
            "two": True,
            "two.three": True,
            "one.four": False,
            "two.three.five": False,
            "six": True,
            "six.seven": True,
            "six.seven.eight": False,
        },
        "/two/three": {
            "one": False,
            "two": True,
            "two.three": True,
            "one.four": False,
            "two.three.five": False,
            "six": True,
            "six.seven": True,
            "six.seven.eight": False,
        },
        "/one/four": {
            "one": False,
            "two": True,
            "two.three": True,
            "one.four": False,
            "two.three.five": False,
            "six": True,
            "six.seven": True,
            "six.seven.eight": False,
        },
        "/one/four/five": {
            "one": False,
            "two": True,
            "two.three": True,
            "one.four": False,
            "two.three.five": False,
            "six": True,
            "six.seven": True,
            "six.seven.eight": False,
        },
        "/six": {
            "one": False,
            "two": True,
            "two.three": True,
            "one.four": False,
            "two.three.five": False,
            "six": True,
            "six.seven": True,
            "six.seven.eight": False,
        },
        "/six/seven": {
            "one": False,
            "two": True,
            "two.three": True,
            "one.four": False,
            "two.three.five": False,
            "six": True,
            "six.seven": True,
            "six.seven.eight": False,
        },
        "/six/seven/eight": {
            "one": False,
            "two": True,
            "two.three": True,
            "one.four": False,
            "two.three.five": False,
            "six": True,
            "six.seven": True,
            "six.seven.eight": False,
        },
    }

    def assert_msg(visible_is):
        path_msg = f"path={path}"
        submenu_msg = "submenu_by_endpoint={endpoint}"
        is_msg = "visible_is={visible_is}"
        should_msg = "visible_should={visible_should}"
        return f"{path_msg} {submenu_msg} {is_msg} {should_msg}"

    for path, v in data.items():
        with app.test_client() as c:
            c.get(path)
            for endpoint, visible_should in v.items():
                visible_is = current_menu.submenu(endpoint).has_visible_child()

                assert visible_is == visible_should, assert_msg(visible_is)


def test_active_checks_segment_not_prefix(app):
    """Test active checks segment not prefix."""

    @app.route("/object")
    @register_menu(app, "object", "Object")
    def object():
        return "object"

    @app.route("/objects")
    @register_menu(app, "objects", "Objects")
    def objects():
        return "objects"

    with app.test_client() as c:
        c.get("/objects")
        assert current_menu.submenu("object").active is not True
