# -*- coding: utf-8 -*-
#
# This file is part of Flask-Menu
# Copyright (C) 2015 CERN.
#
# Flask-Menu is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""A simple demo application showing Flask-Menu in action.

Usage:
  $ fig up
  $ firefox http://0.0.0.0:5000/
  $ firefox http://0.0.0.0:5000/first
  $ firefox http://0.0.0.0:5000/second
"""

from flask import Flask, render_template_string

import flask_menu as menu

app = Flask(__name__)
menu.Menu(app=app)


def tmpl_show_menu():
    """Show menu with current page decorated by asterisk."""
    return render_template_string(
        """
        {%- for item in current_menu.children %}
            {% if item.active %}*{% endif %}{{ item.text }}
        {% endfor -%}
        """)


@app.route('/')
@menu.register_menu(app, '.', 'Home')
def index():
    """Home page."""
    return tmpl_show_menu()


@app.route('/first')
@menu.register_menu(app, '.first', 'First', order=0)
def first():
    """First page."""
    return tmpl_show_menu()


@app.route('/second')
@menu.register_menu(app, '.second', 'Second', order=1)
def second():
    """Second page."""
    return tmpl_show_menu()


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
