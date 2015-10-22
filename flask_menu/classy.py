# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2015 CERN.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Add support for Flask-Classy."""

import inspect

from flask import Blueprint

from flask_menu import current_menu


def register_flaskview(app, classy_view):
    """Register a Flask-Classy FlaskView's menu items with the menu register.

    Example::

        bp = Blueprint('bp', __name__)
        menu.register_flaskview(bp, MyEndpoint)

    :param app: Application or Blueprint which owns the
        function view.
    :param classy_view: The Flask-Classy FlaskView class to register
        menu items for.
    """
    if isinstance(app, Blueprint):
        endpoint_prefix = app.name + '.'
        before_first_request = app.before_app_first_request
    else:
        endpoint_prefix = ''
        before_first_request = app.before_first_request

    @before_first_request
    def _register_menu_items():
        for meth_str in dir(classy_view):
            meth = getattr(classy_view, meth_str)

            if hasattr(meth, '_menu_items'):
                for menu_item in meth._menu_items:
                    endpoint = "{0}{1}:{2}".format(
                        endpoint_prefix,
                        classy_view.__name__,
                        meth.__name__
                    )
                    path = menu_item.pop('path')
                    item = current_menu.submenu(path)
                    item.register(
                        endpoint,
                        **menu_item
                    )


def classy_menu_item(path, text, **kwargs):
    """Decorator to register an endpoint within a Flask-Classy class.

    All usage is otherwise the same to `register_menu`, however you do not need
    to provide reference to the blueprint/app.

    Example::

        class MyEndpoint(FlaskView):
            route_base = '/'

            @menu.classy_menu_item('frontend.account', 'Home', order=0)
            def index(self):
                # Do something.
                pass

    :param path: Path to this item in menu hierarchy,
        for example 'main.category.item'. Path can be an object
        with custom __str__ method: it will be converted on first request,
        therefore you can use current_app inside this __str__ method.
    :param text: Text displayed as link.
    :param order: Index of item among other items in the same menu.
    :param endpoint_arguments_constructor: Function returning dict of
        arguments passed to url_for when creating the link.
    :param active_when: Function returning True when the item
        should be displayed as active.
    :param visible_when: Function returning True when this item
        should be displayed.
    :param dynamic_list_constructor: Function returning a list of
        entries to be displayed by this item. Every object should
        have 'text' and 'url' properties/dict elements. This property
        will not be directly affect the menu system, but allows
        other systems to use it while rendering.
    :param kwargs: Additional arguments will be available as attributes
        on registered :class:`flask_menu.MenuEntryMixin` instance.

    .. versionchanged:: 0.2.0
       The *kwargs* arguments.
    """
    def func_wrap(f):
        expected = inspect.getargspec(f).args
        if 'self' in expected:
            expected.remove('self')
        item = dict(path=path, text=text, expected_args=expected, **kwargs)

        if hasattr(f, '_menu_items'):
            f._menu_items.append(item)
        else:
            f._menu_items = [item]

        return f

    return func_wrap

__all__ = ('register_flaskview', 'classy_menu_item')
