# -*- coding: utf-8 -*-
# This file is part of Flask-Menu
# Copyright (C) 2013, 2014, 2015, 2017 CERN
# Copyright (C) 2017 Marlin Forbes
# Copyright (C) 2023 Graz University of Technology.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Register menu."""

from inspect import getfullargspec

from flask import Blueprint

from .proxies import current_menu


def register_menu(
    app,
    path,
    text,
    order=0,
    endpoint_arguments_constructor=None,
    dynamic_list_constructor=None,
    active_when=None,
    visible_when=None,
    **kwargs,
):
    """Decorate endpoints that should be displayed in a menu.

    Example::

        @register_menu(app, '.', _('Home'))
        def index():
            pass

    :param app: Application or Blueprint which owns the
        function view.
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
        on registered :class:`MenuEntryMixin` instance.

    .. versionchanged:: 0.2.0
       The *kwargs* arguments.
    """

    def menu_decorator(f):
        """Decorator of a view function that should be included in the menu."""
        if isinstance(app, Blueprint):
            endpoint = app.name + "." + f.__name__
            before_first_request = app.before_app_first_request
        else:
            endpoint = f.__name__
            before_first_request = app.before_first_request

        expected = getfullargspec(f).args

        @before_first_request
        def _register_menu_item():
            # str(path) allows path to be a string-convertible object
            # that may be useful for delayed evaluation of path
            item = current_menu.submenu(str(path))
            item.register(
                endpoint,
                text,
                order,
                endpoint_arguments_constructor=endpoint_arguments_constructor,
                dynamic_list_constructor=dynamic_list_constructor,
                active_when=active_when,
                visible_when=visible_when,
                expected_args=expected,
                **kwargs,
            )

        return f

    return menu_decorator
