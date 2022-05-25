from flask import Flask, render_template
import flask_menu as menu

app = Flask(__name__, template_folder='')
menu.Menu(app=app)

@app.route('/')
@menu.register_menu(app, '.', 'Home')
def index():
    return render_template('index.html')

@app.route('/first')
@menu.register_menu(app, '.first', 'First', order=0)
def first():
    return render_template('index.html')

@app.route('/second')
@menu.register_menu(app, '.second', 'Second', order=1)
def second():
    ids = [1, 2, 3, 4, 5]
    details_route = 'second_details'
    return render_template('index.html', 
        context={'ids': ids, 'details_route': details_route}
    )

@app.route('/second/<int:id>')
@menu.register_menu(app, '.second.details', 'Details', id=id)
def second_details(id):
    headline = f'Details of Second id: {id}'
    details = f'Here are more details for Second id: {id}'
    return render_template('index.html', 
        context={'headline': headline, 'details': details}
    )

@app.route('/third')
@menu.register_menu(app, '.third', 'Third', order=3, dropdown=True)
def third():
    ids = [1, 2, 3]
    details_route = 'third_details'
    return render_template('index.html', 
        context={'ids': ids, 'details_route': details_route}
    )

@app.route('/third/<int:id>')
@menu.register_menu(app, '.third.details', 'Details', id=id, hide_on_menu=True)
def third_details(id):
    headline = f'Details of Third id: {id}'
    details = f'Here are more details for Third id: {id}'
    return render_template('index.html', 
        context={'headline': headline, 'details': details}
    )

@app.route('/third/a')
@menu.register_menu(app, '.third.a', 'A')
def third_a():
    ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    details_route = 'third_a_details'
    return render_template('index.html', 
        context={'ids': ids, 'details_route': details_route}
    )

@app.route('/third/b')
@menu.register_menu(app, '.third.b', 'B')
def third_b():
    return render_template('index.html')

@app.route('/third/a/<int:id>')
@menu.register_menu(app, '.third.a.details', 'Details', id=id)
def third_a_details(id):
    headline = f'Details of Third A id: {id}'
    details = f'Here are more details for Third A id: {id}'
    return render_template('index.html',
        context={'headline': headline, 'details': details}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)