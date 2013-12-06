.. _quickstart:

Quickstart
==========

This guide assumes you have successfully installed Flask-Menu and
a working Flask application. If not, follow the Flask Quickstart guide.


A Minimal Example
-----------------

A minimal Flask-Menu usage looks like this: ::

    from flask import Flask
    from flask.ext import menu

    app = Flask(__name__)

    # Initialize Flask-Menu
    menu.Menu(app=app)

    @app.route('/')
    @menu.register_menu(app, '.', 'Home')
    def index():
        pass

    if __name__ == '__main__':
        app.run(debug=True)


Save this as app.py and run it using your Python interpreter. ::

    $ python app.py
     * Running on http://127.0.0.1:5000/

