# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2013, 2014, 2015, 2017 CERN
# Copyright (C) 2017 Marlin Forbes
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""This extension allows creation of menus organised in a tree structure.

Those menus can be then displayed using templates.
"""

import inspect
import types

from flask import Blueprint, current_app, request, url_for, g
from six import PY3

from werkzeug.local import LocalProxy

from .version import __version__


def CONDITION_TRUE(*args, **kwargs):
    """Return always True."""
    return True


def CONDITION_FALSE(*args, **kwargs):
    """Return always False."""
    return False


class Menu(object):
    """Flask extension implementation."""

    def __init__(self, app=None):
        """Initialize Menu extension."""
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize a Flask application."""
        self.app = app
        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'menu' in app.extensions:
            raise RuntimeError("Flask application is already initialized.")
        app.extensions['menu'] = MenuEntryMixin('', None)

        app.context_processor(lambda: dict(
            current_menu=current_menu))

        @app.url_value_preprocessor
        def url_preprocessor(route, args):
            """Store the current route endpoint and arguments."""
            g._menu_kwargs = args
            g._menu_route = route

    @staticmethod
    def root():
        """Return a root entry of current application's menu."""
        return current_app.extensions['menu']


class MenuEntryMixin(object):
    """Represent a entry node in the menu tree.

    Provides information for displaying links (text, url, visible, active).
    Navigate the hierarchy using :meth:`children` and :meth:`submenu`.
    """

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

        self._child_entries = dict()
        self._endpoint = None
        self._text = None
        self._order = 0
        self._external_url = None
        self._endpoint_arguments_constructor = None
        self._dynamic_list_constructor = None
        self._visible_when = CONDITION_TRUE
        self._expected_args = []

    def _active_when(self):
        """Define condition when a menu entry is active."""
        matching_endpoint = request.endpoint == self._endpoint

        def segments(path):
            """Split a path into segments."""
            parts = path.split('/')[1:]
            if len(parts) > 0 and parts[-1] == '':
                parts.pop()
            return parts

        if len(self.url) > 1:
            segments_url = segments(self.url)
            segments_request = segments(request.path)
            matching_segments = \
                segments_request[0:len(segments_url)] == segments_url
        else:
            matching_segments = False
        matching_completpath = request.path == self.url
        return matching_endpoint or matching_segments or matching_completpath

    def register(self, endpoint=None, text=None, order=0, external_url=None,
                 endpoint_arguments_constructor=None,
                 dynamic_list_constructor=None,
                 active_when=None,
                 visible_when=None,
                 expected_args=None,
                 **kwargs):
        """Assign endpoint and display values.

        .. versionadded:: 0.6.0
           The *external_url* parameter is mutually exclusive with *endpoint*.
        """
        if endpoint is not None and external_url is not None:
            raise TypeError('Exclusive arguments endpoint and external_url.')

        self._endpoint = endpoint
        self._text = text or self.name
        self._order = order
        self._external_url = external_url
        self._expected_args = expected_args or []
        self._endpoint_arguments_constructor = endpoint_arguments_constructor
        self._dynamic_list_constructor = dynamic_list_constructor
        if active_when is not None:
            active_when_param = inspect.getfullargspec(active_when)[0] \
                if PY3 else inspect.getargspec(active_when)[0]
            if len(active_when_param) == 1:
                self._active_when = types.MethodType(active_when, self)
            else:
                self._active_when = active_when
        if visible_when is not None:
            self._visible_when = visible_when

        for key, value in kwargs.items():
            if hasattr(self, key):
                raise RuntimeError('Can not override existing attribute '
                                   '{0}.'.format(key))
            setattr(self, key, value)

    def submenu(self, path, auto_create=True):
        """Return submenu placed at the given path in the hierarchy.

        If it does not exist, a new one is created. Return None if path
        string is invalid.

        :param path: Path to submenu as a string 'qua.bua.cua'
        :param auto_create: If True, missing entries will be created
            to satisfy the given path.
        :return: Submenu placed at the given path in the hierarchy.
        """
        if not path or path in ['.', '']:
            return self

        (path_head, dot, path_tail) = path.partition('.')

        if path_head == '':
            next_entry = self
        elif path_head not in self._child_entries:
            # Create the entry if it does not exist
            if auto_create:
                # The entry was not found so create a new one
                next_entry = self._child_entries[path_head] = \
                    MenuEntryMixin(path_head, self)
            else:
                # The entry was not found, but we are forbidden to create
                return None
        else:
            next_entry = self._child_entries[path_head]

        if path_tail:
            return next_entry.submenu(path_tail, auto_create)
        else:
            # that was the last part of the path
            return next_entry

    def list_path(self, from_path, to_path):
        """Return all items on path between two specified entries.

        Only if one of them is an ancestor of the other.

        :param from_path: The ancestor entry.
        :param to_path: The child entry.

        :return: List of entries between those items or None if
            they are on different branches.
        """
        ancestor_entry = self.submenu(from_path, auto_create=False)
        child_entry = self.submenu(to_path, auto_create=False)

        if not (ancestor_entry and child_entry):
            # Incorrect paths
            return None

        branch_list = [child_entry]
        while (child_entry.parent is not None) \
                and (child_entry != ancestor_entry):
            child_entry = child_entry.parent
            branch_list.append(child_entry)

        # This means the search reached root, but the ancestor
        # was not encountered. Therefore, entries are on different branches.
        if branch_list[-1] != ancestor_entry:
            return None
        else:
            branch_list.reverse()
            return branch_list

    def hide(self):
        """Make the entry always hidden."""
        self._visible_when = CONDITION_FALSE

    @property
    def active_item(self):
        """Return the active item from the menu's tree.

        Return self if the item itself is active. Return an
        active child if there is one. If there are no active menu items,
        None will be returned.
        """
        for child in self.children:
            active = child.active_item
            if active is not None:
                return active

        if self.active:
            return self

        return None

    @property
    def dynamic_list(self):
        """Return list from dynamic list constructor."""
        if self._dynamic_list_constructor:
            return self._dynamic_list_constructor()
        else:
            return [self]

    @property
    def order(self):
        return self._order

    @property
    def children(self):
        """Return list of sorted children."""
        return sorted(self._child_entries.values(),
                      key=lambda entry: getattr(entry, 'order', 0))

    @property
    def text(self):
        return self._text or 'Menu item not initialised'

    @property
    def url(self):
        """Generate url from given endpoint and optional dynamic arguments."""
        if not self._endpoint:
            return self._external_url or '#'

        if self._endpoint_arguments_constructor:
            return url_for(self._endpoint,
                           **self._endpoint_arguments_constructor())

        # Inject current args. Allows usage when inside a blueprint with a url
        # param.
        # Filter out any arguments which don't need to be passed.
        args = {}
        if hasattr(g, '_menu_kwargs') and g._menu_kwargs:
            for key in g._menu_kwargs:
                if key in self._expected_args:
                    args[key] = g._menu_kwargs[key]

        return url_for(self._endpoint, **args)

    @property
    def active(self):
        """Return True if the menu item is active."""
        return self._active_when()

    @property
    def visible(self):
        """Return True if the menu item is visible."""
        return self._text is not None and self._visible_when()

    def has_active_child(self, recursive=True):
        """Return True if the menu has an active child."""
        for child in self._child_entries.values():
            if child.active:
                return True
        if recursive:
            for child in self._child_entries.values():
                if child.has_active_child(recursive=recursive):
                    return True
        return False

    def has_visible_child(self, recursive=True):
        """Return True if the menu has a visible child."""
        result = False
        for child in self._child_entries.values():
            if child.visible:
                return True

        if recursive:
            for child in self._child_entries.values():
                if child.visible or child.has_visible_child(recursive=True):
                    return True

        return False


def register_menu(app, path, text, order=0,
                  endpoint_arguments_constructor=None,
                  dynamic_list_constructor=None,
                  active_when=None,
                  visible_when=None,
                  **kwargs):
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
            endpoint = app.name + '.' + f.__name__
            before_first_request = app.before_app_first_request
        else:
            endpoint = f.__name__
            before_first_request = app.before_first_request

        expected = inspect.getfullargspec(f).args if PY3 else \
            inspect.getargspec(f).args

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
                **kwargs)
        return f

    return menu_decorator


#: Global object that is proxy to the current application menu.
current_menu = LocalProxy(Menu.root)

__all__ = ('current_menu', 'register_menu', 'Menu', '__version__')
