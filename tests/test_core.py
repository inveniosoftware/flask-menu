# -*- coding: utf-8 -*-
##
## This file is part of Flask-Menu
## Copyright (C) 2013, 2014 CERN.
##
## Flask-Menu is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Flask-Menu is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Flask-Menu; if not, write to the Free Software Foundation,
## Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
##
## In applying this licence, CERN does not waive the privileges and immunities
## granted to it by virtue of its status as an Intergovernmental Organization
## or submit itself to any jurisdiction.

import sys
from unittest import TestCase
from flask import Blueprint, Flask, request, url_for

from flask.ext.menu import Menu, current_menu, register_menu


class FlaskTestCase(TestCase):
    """
    Mix-in class for creating the Flask application
    """

    def setUp(self):
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.logger.disabled = True
        self.app = app

    def tearDown(self):
        self.app = None


class TestMenu(FlaskTestCase):

    def test_simple_app(self):
        Menu(self.app)

        @self.app.route('/test')
        @register_menu(self.app, '.', 'Test')
        def test():
            return 'test'

        @self.app.route('/level2')
        @register_menu(self.app, 'level2', 'Level 2')
        def level2():
            return 'level2'

        @self.app.route('/level3')
        @register_menu(self.app, 'level2.level3', 'Level 3', order=2)
        def level3():
            return 'level3'

        @self.app.route('/level3B')
        @register_menu(self.app, 'level2.level3B', 'Level 3B', order=1)
        def level3B():
            return 'level3B'

        with self.app.test_client() as c:
            c.get('/test')
            assert request.endpoint == 'test'
            assert current_menu.url == '/test'
            assert current_menu.text == 'Test'
            assert current_menu.active
            self.assertEqual(current_menu.submenu('level2').text, 'Level 2')
            assert not current_menu.submenu('level2').active
            assert current_menu.submenu('missing', auto_create=False) is None
            assert len(current_menu.list_path('.', '.level2.level3')) == 3
            assert current_menu.list_path('.', 'missing') is None
            assert current_menu.list_path('missing', '.level2.level3') is None
            assert current_menu.list_path('level2.level3B',
                                          'level2.level3') is None

        with self.app.test_client() as c:
            c.get('/level2')
            assert current_menu.submenu('level2').active

        with self.app.test_client() as c:
            c.get('/level3')
            assert current_menu.submenu('.level2.level3').active
            assert current_menu.submenu('level2.level3').active
            item_2 = current_menu.submenu('level2.level3')
            item_1 = current_menu.submenu('level2.level3B')
            assert item_1.order < item_2.order
            assert item_1 == current_menu.submenu('level2').children[0]
            assert item_2 == current_menu.submenu('level2').children[1]

    # The following test is known to fail on Python 3.4.0 while it
    # works well on lesser or higher Pythons.  (Additionally cannot
    # use unittest.skipIf() here due to Python-2.6.)
    if sys.version_info != (3, 4, 0, 'final', 0):
        def test_blueprint(self):
            Menu(self.app)
            blueprint = Blueprint('foo', 'foo', url_prefix="/foo")

            @self.app.route('/test')
            @register_menu(self.app, '.', 'Test')
            def test():
                return 'test'

            @blueprint.route('/bar')
            @register_menu(blueprint, 'bar', 'Foo Bar')
            def bar():
                return 'bar'

            self.app.register_blueprint(blueprint)

            with self.app.test_client() as c:
                c.get('/test')
                assert request.endpoint == 'test'
                assert current_menu.text == 'Test'

            with self.app.test_client() as c:
                c.get('/foo/bar')
                self.assertEqual(current_menu.submenu('bar').text, 'Foo Bar')
                self.assertTrue(current_menu.submenu('bar').active)

    def test_visible_when(self):
        Menu(self.app)

        @self.app.route('/always')
        @register_menu(self.app, 'always', 'Always', visible_when=lambda: True)
        def always():
            return 'never'

        @self.app.route('/never')
        @register_menu(self.app, 'never', 'Never', visible_when=lambda: False)
        def never():
            return 'never'

        @self.app.route('/normal')
        @register_menu(self.app, 'normal', 'Normal')
        def normal():
            return 'normal'

        data = {
            'never': {'never': False, 'always': True, 'normal': True},
            'always': {'never': False, 'always': True, 'normal': True},
            'normal': {'never': False, 'always': True, 'normal': True},
        }
        for (k, v) in data.items():
            with self.app.test_client() as c:
                c.get('/' + k)
                for (endpoint, visible) in v.items():
                    self.assertEqual(current_menu.submenu(endpoint).visible,
                                     visible)

        with self.app.test_request_context():
            current_menu.submenu('always').hide()

        data = {
            'never': {'never': False, 'always': False, 'normal': True},
            'always': {'never': False, 'always': False, 'normal': True},
            'normal': {'never': False, 'always': False, 'normal': True},
        }
        for (k, v) in data.items():
            with self.app.test_client() as c:
                c.get('/' + k)
                for (endpoint, visible) in v.items():
                    self.assertEqual(current_menu.submenu(endpoint).visible,
                                     visible)

    def test_active_when(self):
        Menu(self.app)

        @self.app.route('/always')
        @register_menu(self.app, 'always', 'Always', active_when=lambda: True)
        def always():
            return 'never'

        @self.app.route('/never')
        @register_menu(self.app, 'never', 'Never', active_when=lambda: False)
        def never():
            return 'never'

        @self.app.route('/normal')
        @register_menu(self.app, 'normal', 'Normal')
        def normal():
            return 'normal'

        data = {
            'never': {'never': False, 'always': True, 'normal': False},
            'always': {'never': False, 'always': True, 'normal': False},
            'normal': {'never': False, 'always': True, 'normal': True},
        }
        for (k, v) in data.items():
            with self.app.test_client() as c:
                c.get('/' + k)
                for (endpoint, active) in v.items():
                    self.assertEqual(current_menu.submenu(endpoint).active,
                                     active)

    def test_dynamic_url(self):
        Menu(self.app)

        @self.app.route('/<int:id>/<string:name>')
        @register_menu(self.app, 'test', 'Test',
                       endpoint_arguments_constructor=lambda: {
                           'id': request.view_args['id'],
                           'name': request.view_args['name'],
                           })
        def test(id, name):
            return str(id) + ':' + name

        with self.app.test_request_context():
            url = url_for('test', id=1, name='foo')

        with self.app.test_client() as c:
            c.get(url)
            assert url == current_menu.submenu('test').url
            assert current_menu.submenu('missing').url == '#'
