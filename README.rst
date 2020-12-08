============
 Flask-Menu
============

.. image:: https://github.com/inveniosoftware/flask-menu/workflows/CI/badge.svg
    :target: https://github.com/inveniosoftware/flask-menu/actions
.. image:: https://coveralls.io/repos/inveniosoftware/flask-menu/badge.png?branch=master
    :target: https://coveralls.io/r/inveniosoftware/flask-menu
.. image:: https://pypip.in/v/Flask-Menu/badge.png
    :target: https://pypi.python.org/pypi/Flask-Menu/
.. image:: https://pypip.in/d/Flask-Menu/badge.png
    :target: https://pypi.python.org/pypi/Flask-Menu/

About
=====
Flask-Menu is a Flask extension that adds support for generating
menus.

Installation
============
Flask-Menu is on PyPI so all you need is: ::

    pip install Flask-Menu

Documentation
=============
Documentation is readable at https://flask-menu.readthedocs.io/ or can be
build using Sphinx: ::

    git submodule init
    git submodule update
    pip install Sphinx
    python setup.py build_sphinx

Testing
=======
Running the test suite is as simple as: ::

    python setup.py test

or, to also show code coverage: ::

    ./run-tests.sh
