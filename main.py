from flask import Flask
from flask import Response
from flask import request
from flask import render_template
from random import shuffle


app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
@app.route('/default.html')
def root():
    founder_list = [
        'Hanzala',
        'David',
        'Derrick',
        'Erasto'
     ] # this assumes that for name there is an image file at /static/images/name.png
    shuffle(founder_list) # random order of pics bc why not
    return render_template('index.html', title='Home', names=founder_list)

@app.route('/roomieQuiz')
@app.route('/roomieQuiz.html')
def questionnaire():
    return render_template('roomieQuiz.html', title='Questionnaire')

@app.route('/DisplayQuestionnaire')
def DisplayQuestionnaire():
    try:
        name = request.args["name"]
        prsntype ="Personality Type: %s" % (request.args["type"])
        pet = "Pet Policy: %s" % (request.args["pet"])
        smoke = "Smoke Policy: %s" % (request.args["smoke"])
        friends = "Friend Policy: %s" % (request.args["friends"])
        bedtime = "Bedtime: %s" % (request.args["bedtime"])

        list = [prsntype, pet, smoke, friends, bedtime]

        return render_template('quizResults.html', title = "Results", Name = name, results = list)
    except:
        return questionnaire()

@app.errorhandler(404)
@app.route('/404.html')
@app.route('/404')
def error404(e):
    return render_template('404.html', title='404'), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
