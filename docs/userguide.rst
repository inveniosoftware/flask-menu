.. _templating:

Templating
==========

By default, a proxy object to `current_menu` is added to your Jinja2
context as `current_menu` to help you with creating navigation bar.
For example: ::

    <ul>
    {%- for item in current_menu -%}
        <li>
        <a href="{{ item.url}}">{{ item.text }}</a>
        {%- if item.children -%}
        <ul>
            {{ loop(item.children) }}
        </ul>
        {%- endif -%}
        </li>
    {%- endfor -%}
    </ul>

.. _blueprints:

Blueprint Support
=================

The most import part of an modular Flask application is Blueprint. You
can create one for your application somewhere in your code and decorate
your view function, like this: ::

    from flask import Blueprint
    from flask.ext import menu

    bp_account = Blueprint('account', __name__, url_prefix='/account')

    @bp_account.route('/')
    @menu.register_menu(bp_account, '.account', 'Your account')
    def index():
        pass


Sometimes you want to combine multiple blueprints and organize the
navigation to certain hierarchy. ::

    from flask import Blueprint
    from flask.ext import breadcrumbs

    bp_social = Blueprint('social', __name__, url_prefix='/social')

    @bp_account.route('/list')
    @menu.register_menu(bp_social, '.account.list', 'Social networks')
    def list():
        pass

As a result of this, your `current_breadcrumbs` object with contain list
with 3 items during processing request for `/social/list`. ::

    >>> from example import app
    >>> from flask.ext import menu
    >>> import account
    >>> import social
    >>> app.register_blueprint(account.bp_account)
    >>> app.register_blueprint(social.bp_social)
    >>> with app.test_client() as c:
    ...     c.get('/social/list')
    ...     assert current_menu.submenu('account.list').active
    ...     current_menu.children

