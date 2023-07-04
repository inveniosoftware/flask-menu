============
 Flask-Menu
============
.. currentmodule:: flask_menu

.. raw:: html

    <p style="height:22px; margin:0 0 0 2em; float:right">
        <a href="https://github.com/inveniosoftware/flask-menu/actions">
            <img src="https://github.com/inveniosoftware/flask-menu/workflows/CI/badge.svg"
                 alt="github-ci badge"/>
        </a>
        <a href="https://coveralls.io/r/inveniosoftware/flask-menu">
            <img src="https://coveralls.io/repos/inveniosoftware/flask-menu/badge.png?branch=master"
                 alt="coveralls.io badge"/>
        </a>
    </p>


Flask-Menu is a Flask extension that adds support for generating menus.

Contents
--------

.. contents::
   :local:
   :depth: 1
   :backlinks: none


.. _installation:

Installation
============

Flask-Menu is on PyPI so all you need is:

.. code-block:: console

    $ pip install Flask-Menu

The development version can be downloaded from `its page at GitHub
<http://github.com/inveniosoftware/flask-menu>`_.

.. code-block:: console

    $ git clone https://github.com/inveniosoftware/flask-menu.git
    $ cd flask-menu
    $ python setup.py develop
    $ ./run-tests.sh

Requirements
^^^^^^^^^^^^

Flask-Menu has the following dependencies:

* `Flask <https://pypi.python.org/pypi/Flask>`_

Flask-Menu requires Python version 3.7


.. _usage:

Usage
=====

This guide assumes that you have successfully installed ``Flask-Menu``
package already.  If not, please follow the :ref:`installation`
instructions first.

Simple Example
^^^^^^^^^^^^^^

Here is a simple Flask-Menu usage example:

.. code-block:: python

    from flask import Flask
    from flask import render_template_string
    from flask_menu import Menu

    app = Flask(__name__)
    Menu(app=app)

    def init(app):
        menu = app.extensions["menu"]
        menu.submenu(".").register("index", "Home")
        menu.submenu(".first").register("first", "First")
        menu.submenu(".second").register("second", "Second", order=1)

    def tmpl_show_menu():
        return render_template_string(
            """
            {%- for item in current_menu.children %}
                {% if item.active %}*{% endif %}{{ item.text }}
            {% endfor -%}
            """)

    @app.route('/')
    def index():
        return tmpl_show_menu()

    @app.route('/first')
    def first():
        return tmpl_show_menu()

    @app.route('/second')
    def second():
        return tmpl_show_menu()

    if __name__ == '__main__':
        init(app)
        app.run(debug=True)

If you save the above as ``app.py``, you can run the example
application using your Python interpreter:

.. code-block:: console

    $ python app.py
     * Running on http://127.0.0.1:5000/

and you can observe generated menu on the example pages:

.. code-block:: console

    $ firefox http://127.0.0.1:5000/
    $ firefox http://127.0.0.1:5000/first
    $ firefox http://127.0.0.1:5000/second

You should now be able to emulate this example in your own Flask
applications.  For more information, please read the :ref:`templating`
guide, the :ref:`blueprints` guide, and peruse the :ref:`api`.


.. _templating:

Templating
==========

By default, a proxy object to `current_menu` is added to your Jinja2
context as `current_menu` to help you with creating navigation bar.
For example:

.. code-block:: jinja

    <ul>
      {%- for item in current_menu.children recursive -%}
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
your view function, like this:

.. code-block:: python

    from flask import Blueprint
    from flask_menu import current_menu

    bp_account = Blueprint('account', __name__, url_prefix='/account')
    current_menu.submenu(".account").register("account.index", "Your account")

    @bp_account.route('/')
    def index():
        pass


Sometimes you want to combine multiple blueprints and organize the
navigation to certain hierarchy.

.. code-block:: python

    from flask import Blueprint
    from flask_menu import current_menu

    bp_social = Blueprint('social', __name__, url_prefix='/social')

    current_menu.submenu(".account.list").register("social.list", "Social networks")

    @bp_account.route('/list')
    def list():
        pass

As a result of this, your `current_menu` object will contain a list
with 3 items while processing a request for `/social/list`.

.. code-block:: python

    >>> from example import app
    >>> from flask_menu import current_menu
    >>> import account
    >>> import social
    >>> app.register_blueprint(account.bp_account)
    >>> app.register_blueprint(social.bp_social)
    >>> with app.test_client() as c:
    ...     c.get('/social/list')
    ...     assert current_menu.submenu('account.list').active
    ...     current_menu.children


.. _api:

API
===

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

Flask extension
^^^^^^^^^^^^^^^

.. module:: flask_menu

.. autoclass:: Menu
   :members:

.. autoclass:: MenuNode
   :members:


Proxies
^^^^^^^

.. data:: current_menu

   Root of a menu item.


.. include:: ../CHANGES.rst

.. include:: ../CONTRIBUTING.rst

License
=======

.. include:: ../LICENSE

.. include:: ../AUTHORS.rst
