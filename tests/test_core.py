# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

import sys
from unittest import TestCase, skipIf

from flask import Blueprint, Flask, request, url_for

from flask_menu import Menu, current_menu, register_menu
from flask_menu.classy import classy_menu_item, register_flaskview


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

            assert not current_menu.has_active_child(recursive=False)
            assert current_menu.has_active_child()
            assert current_menu.submenu('level2').has_active_child(
                recursive=False)
            assert current_menu.submenu('level2').has_active_child()

            item_2 = current_menu.submenu('level2.level3')
            item_1 = current_menu.submenu('level2.level3B')
            assert item_1.order < item_2.order
            assert item_1 == current_menu.submenu('level2').children[0]
            assert item_2 == current_menu.submenu('level2').children[1]

    @skipIf(sys.version_info == (3, 4, 0, 'final', 0) or
            sys.version_info == (3, 4, 1, 'final', 0),
            'This test is known to fail on Python 3.4.0 and 3.4.1'
            'but works on earlier and later versions.')
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
            self.assertEqual(
                current_menu.submenu('bar').text, 'Foo Bar')
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

    def test_visible_when_with_dynamic(self):
        Menu(self.app)

        @self.app.route('/always')
        @register_menu(self.app, 'always', 'Always', visible_when=lambda: True)
        def always():
            return 'never'

        @self.app.route('/never')
        @register_menu(self.app, 'never', 'Never', visible_when=lambda: False)
        def never():
            return 'never'

        @register_menu(self.app, 'normal', 'Normal')
        @self.app.route('/normal/<int:id>/')
        def normal(id):
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

    def test_active_item(self):
        """Test active_item method."""
        Menu(self.app)

        @self.app.route('/')
        @register_menu(self.app, 'root', 'root')
        def root():
            return "root"

        @self.app.route('/sub1/item1')
        @register_menu(self.app, 'root.sub1.item1', 'Sub 1 - Item 1')
        def sub1_item1():
            return "sub1_item1"

        @self.app.route('/sub2/item1')
        @register_menu(self.app, 'root.sub2.item1', 'Sub 2 - Item 1')
        def sub2_item1():
            return "sub2_item1"

        @self.app.route('/sub2/item2')
        @register_menu(self.app, 'root.sub2.item2', 'Sub 2 - Item 2')
        def sub2_item2():
            return "sub2_item2"

        with self.app.test_client() as c:
            c.get('/')
            self.assertEqual(
                current_menu.active_item, current_menu.submenu('root'))
            c.get('/sub1/item1')
            self.assertEqual(current_menu.active_item,
                             current_menu.submenu('root.sub1.item1'))
            sub1 = current_menu.submenu('root.sub1')
            self.assertEqual(sub1.active_item,
                             current_menu.submenu('root.sub1.item1'))
            sub2 = current_menu.submenu('root.sub2')
            self.assertIsNone(sub2.active_item)
            c.get('/sub2/item2')
            self.assertEqual(sub2.active_item,
                             current_menu.submenu('root.sub2.item2'))

    def test_active_when(self):
        Menu(self.app)

        @self.app.route('/')
        @register_menu(self.app, 'root', 'Root')
        def root():
            return 'root'

        @self.app.route('/always')
        @register_menu(self.app, 'always', 'Always', active_when=lambda: True)
        def always():
            return 'always'

        @self.app.route('/never')
        @register_menu(self.app, 'never', 'Never', active_when=lambda: False)
        def never():
            return 'never'

        @self.app.route('/normal')
        @self.app.route('/normal/<path:path>')
        @register_menu(
            self.app, 'normal', 'Normal',
            active_when=lambda self: request.endpoint == self._endpoint
        )
        def normal(path=None):
            return 'normal'

        data = {
            '/never': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': False
            },
            '/always': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': False
            },
            '/normal': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': True
            },
            '/normal/foo': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': True
            },
            '/bar/normal': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': False
            },
            '/bar/normal/foo': {
                'root':   False,
                'never':  False,
                'always': True,
                'normal': False
            },
            '/': {
                'root':   True,
                'never':  False,
                'always': True,
                'normal': False
            },
            '': {
                'root':   True,
                'never':  False,
                'always': True,
                'normal': False
            },
        }
        for (path, testset) in data.items():
            with self.app.test_client() as c:
                c.get(path)
                for (endpoint, active_should) in testset.items():
                    active_is = current_menu.submenu(endpoint).active
                    self.assertEqual(
                        active_is,
                        active_should,
                        'path="{0}" submenu_by_endpoint="{1}" '
                        'active_is={2} active_should={3}'.format(
                            path,
                            endpoint,
                            active_is,
                            active_should
                        )
                    )

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

    def test_kwargs(self):
        """Test optional arguments."""
        Menu(self.app)
        count = 5

        @self.app.route('/test')
        @register_menu(self.app, 'test', 'Test', count=count)
        def test():
            return 'count'

        with self.app.test_client() as c:
            c.get('/test')
            assert count == current_menu.submenu('test').count

    def test_kwargs_override(self):
        """Test if optional arguments cannot be overriden."""
        Menu(self.app)

        @self.app.route('/test')
        @register_menu(self.app, 'test', 'Test', url='/test')
        def test():
            pass

        with self.app.test_client() as c:
            self.assertRaises(RuntimeError, c.get, '/test')

    def test_external_url(self):
        """Test that external_url works, and is not overriding endpoint."""
        Menu(self.app)
        menu = self.app.extensions['menu']

        url = 'https://python.org'

        item1 = menu.submenu('menuitem1')

        # Do not allow endpoint and external_url at the same time.
        self.assertRaises(TypeError, item1.register, endpoint='test',
                          text='Test', external_url=url)

        item1.register(text='Test', external_url=url)
        assert menu.submenu('menuitem1').url == url

    def test_double_instantiation(self):
        Menu(self.app)
        self.assertRaises(RuntimeError, Menu, self.app)

    def test_dynamic_url_with_auto_args(self):
        """Ensure url can be generated by inferring args from current route."""
        pass

    def test_dynamic_blueprint_with_auto_args(self):
        pass

    def test_classy_endpoint_on_blueprint(self):
        from flask_classy import FlaskView

        class MyEndpoint(FlaskView):
            route_base = '/'

            def index(self):
                return ''

            @classy_menu_item('page1', 'Page 1')
            def page1(self):
                return ''

            @classy_menu_item('page2', 'Page 2')
            def page2(self):
                return ''

            @classy_menu_item('page3', 'Page 3')
            @classy_menu_item('page31', 'Page 3.1')
            def page3(self):
                return ''

        Menu(self.app)

        bp = Blueprint('foo', 'foo', url_prefix='/foo')

        MyEndpoint.register(bp)
        register_flaskview(bp, MyEndpoint)

        self.app.register_blueprint(bp)

        data = {
            '/foo/page1/': {
                'page1': True,
                'page2': False,
                'page3': False,
                'page31': False
            },
            '/foo/page2/': {
                'page1': False,
                'page2': True,
                'page3': False,
                'page31': False
            },
            '/foo/page3/': {
                'page1': False,
                'page2': False,
                'page3': True,
                'page31': True
            }
        }

        for (path, v) in data.items():
            with self.app.test_client() as c:
                c.get(path)
                for (endpoint, active_should) in v.items():
                    active_is = current_menu.submenu(endpoint).active
                    self.assertEqual(
                        active_is,
                        active_should,
                        'path="{0}" submenu_by_endpoint="{1}" '
                        'active_is={2} active_should={3}'.format(
                            path,
                            endpoint,
                            active_is,
                            active_should
                        )
                    )

    def test_classy_endpoint_with_args(self):
        from flask_classy import FlaskView, route

        class MyEndpoint(FlaskView):
            route_base = '/'

            @classy_menu_item('withid.page1', 'Page 1')
            @route('/<int:id>/page1')
            def page1(self, id):
                return 'page1'

            @classy_menu_item('withid.page2', 'Page 2')
            @route('/<int:id>/page2')
            def page2(self, id):
                return 'page2'

        Menu(self.app)
        MyEndpoint.register(self.app)
        register_flaskview(self.app, MyEndpoint)

        data = {
            '/1/page1': {
                'withid.page1': True,
                'withid.page2': False,
            },
            '/1/page2': {
                'withid.page1': False,
                'withid.page2': True,
            }
        }

        for (path, v) in data.items():
            with self.app.test_client() as c:
                c.get(path)
                for (endpoint, active_should) in v.items():
                    active_is = current_menu.submenu(endpoint).active
                    self.assertEqual(
                        active_is,
                        active_should,
                        'path="{0}" submenu_by_endpoint="{1}" '
                        'active_is={2} active_should={3}'.format(
                            path,
                            endpoint,
                            active_is,
                            active_should
                        )
                    )

    def test_classy_endpoint(self):
        from flask_classy import FlaskView

        class MyEndpoint(FlaskView):
            route_base = '/'

            def index(self):
                return ''

            @classy_menu_item('page1', 'Page 1')
            def page1(self):
                return ''

            @classy_menu_item('page2', 'Page 2')
            def page2(self):
                return ''

            @classy_menu_item('page3', 'Page 3')
            @classy_menu_item('page31', 'Page 3.1')
            def page3(self):
                return ''

        Menu(self.app)
        MyEndpoint.register(self.app)
        register_flaskview(self.app, MyEndpoint)

        data = {
            '/page1/': {
                'page1': True,
                'page2': False,
                'page3': False,
                'page31': False
            },
            '/page2/': {
                'page1': False,
                'page2': True,
                'page3': False,
                'page31': False
            },
            '/page3/': {
                'page1': False,
                'page2': False,
                'page3': True,
                'page31': True
            }
        }

        for (path, v) in data.items():
            with self.app.test_client() as c:
                c.get(path)
                for (endpoint, active_should) in v.items():
                    active_is = current_menu.submenu(endpoint).active
                    self.assertEqual(
                        active_is,
                        active_should,
                        'path="{0}" submenu_by_endpoint="{1}" '
                        'active_is={2} active_should={3}'.format(
                            path,
                            endpoint,
                            active_is,
                            active_should
                        )
                    )

    def test_dynamic_list_constructor(self):

        bar = ['Item 1', 'Item 2', 'Item 3']

        def get_menu_items():
            return bar

        @register_menu(self.app, 'foo', 'foo',
                       dynamic_list_constructor=get_menu_items)
        @self.app.route('/')
        def foo():
            return 'foo'

        @register_menu(self.app, 'other', 'Other')
        @self.app.route('/other')
        def other():
            return 'other'

        Menu(self.app)

        with self.app.test_client() as c:
            c.get('/')
            self.assertEquals(
                current_menu.submenu('foo').dynamic_list,
                bar
            )
            self.assertEquals(
                current_menu.submenu('other').dynamic_list,
                [current_menu.submenu('other')]
            )

    def test_app_without_existing_extensions(self):
        del self.app.extensions
        Menu(self.app)
        self.assertEqual(len(self.app.extensions), 1)

    def test_has_visible_child(self):
        Menu(self.app)

        @self.app.route('/one')
        def one():
            return 'one'

        # This item should never be visible.
        @register_menu(self.app, 'one.four', 'One Four',
                       visible_when=lambda: False)
        @self.app.route('/one/four')
        def one_four():
            return 'one_four'

        @self.app.route('/six')
        def six():
            return 'six'

        # This item should never be visible.
        @register_menu(self.app, 'six.seven', 'Six Seven',
                       visible_when=lambda: False)
        @self.app.route('/six/seven')
        def six_seven():
            return 'six_seven'

        @register_menu(self.app, 'six.seven.eight', 'Six Seven Eight')
        @self.app.route('/six/seven/eight')
        def six_seven_eight():
            return 'six_seven_eight'

        @register_menu(self.app, 'two', 'Two')
        @self.app.route('/two')
        def two():
            return 'two'

        @register_menu(self.app, 'two.three', 'Two Three')
        @self.app.route('/two/three')
        def two_three():
            return 'two_three'

        @register_menu(self.app, 'two.three.five', 'Two Three Five')
        @self.app.route('/two/three/five')
        def two_three_five():
            return 'two_three_five'

        data = {
            '/one': {
                'one': False,
                'two': True,
                'two.three': True,
                'one.four': False,
                'two.three.five': False,
                'six': True,
                'six.seven': True,
                'six.seven.eight': False,
            },
            '/two': {
                'one': False,
                'two': True,
                'two.three': True,
                'one.four': False,
                'two.three.five': False,
                'six': True,
                'six.seven': True,
                'six.seven.eight': False,
            },
            '/two/three': {
                'one': False,
                'two': True,
                'two.three': True,
                'one.four': False,
                'two.three.five': False,
                'six': True,
                'six.seven': True,
                'six.seven.eight': False,
            },
            '/one/four': {
                'one': False,
                'two': True,
                'two.three': True,
                'one.four': False,
                'two.three.five': False,
                'six': True,
                'six.seven': True,
                'six.seven.eight': False,
            },
            '/one/four/five': {
                'one': False,
                'two': True,
                'two.three': True,
                'one.four': False,
                'two.three.five': False,
                'six': True,
                'six.seven': True,
                'six.seven.eight': False,
            },
            '/six': {
                'one': False,
                'two': True,
                'two.three': True,
                'one.four': False,
                'two.three.five': False,
                'six': True,
                'six.seven': True,
                'six.seven.eight': False,
            },
            '/six/seven': {
                'one': False,
                'two': True,
                'two.three': True,
                'one.four': False,
                'two.three.five': False,
                'six': True,
                'six.seven': True,
                'six.seven.eight': False,
            },
            '/six/seven/eight': {
                'one': False,
                'two': True,
                'two.three': True,
                'one.four': False,
                'two.three.five': False,
                'six': True,
                'six.seven': True,
                'six.seven.eight': False,
            }
        }

        for (path, v) in data.items():
            with self.app.test_client() as c:
                c.get(path)
                for (endpoint, visible_should) in v.items():
                    visible_is = current_menu.submenu(
                        endpoint
                    ).has_visible_child()

                    self.assertEqual(
                        visible_is,
                        visible_should,
                        'path="{0}" submenu_by_endpoint="{1}" '
                        'visible_is={2} visible_should={3}'.format(
                            path,
                            endpoint,
                            visible_is,
                            visible_should
                        )
                    )
