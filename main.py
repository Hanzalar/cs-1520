from flask import Flask
from flask import Response
from flask import render_template


app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
@app.route('/default.html')
def root():
    founder_list = {
        'Hanzala',
        'David',
        'Derrick',
        'Erasto'
    } # this assumes that for name there is an image file at /static/images/name.png
    return render_template('index.html', title='Home', names=founder_dict)

@app.errorhandler(404)
@app.route('/404.html')
@app.route('/404')
def error404(e):
    return render_template('404.html', title='404'), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
