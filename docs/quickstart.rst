.. _quickstart:

Quickstart
==========

This guide assumes that you have successfully installed ``Flask-Menu``
package already.  If not, please follow the :ref:`installation`
instructions first.

Simple Example
--------------

Here is a simple Flask-Menu usage example:

.. code-block:: python

    from flask import Flask
    from flask import render_template_string
    from flask.ext import menu

    app = Flask(__name__)
    menu.Menu(app=app)

    def tmpl_show_menu():
        return render_template_string("""
            {% for item in current_menu.children %}
                {% if item.active %}*{% endif %}{{ item.text }}
            {% endfor %}""")

    @app.route('/')
    @menu.register_menu(app, '.', 'Home')
    def index():
        return tmpl_show_menu()

    @app.route('/first')
    @menu.register_menu(app, '.first', 'First', order=0)
    def first():
        return tmpl_show_menu()

    @app.route('/second')
    @menu.register_menu(app, '.second', 'Second', order=1)
    def second():
        return tmpl_show_menu()

    if __name__ == '__main__':
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
