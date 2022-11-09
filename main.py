from flask import Flask
from flask import Response
from flask import request
from flask import render_template
from flask import flash
from random import shuffle
from werkzeug.security import generate_password_hash, check_password_hash
from google.cloud import datastore


app = Flask(__name__)

def create_user():
    client = datastore.Client()
    key = client.key('user')
    return datastore.Entity(key)

@app.route('/')
@app.route('/index.html')
@app.route('/default.html')
def root():
    alert_msg = None
    founder_list = [
        'Hanzala',
        'David',
        'Derrick',
        'Erasto'
     ] # this assumes that for name there is an image file at /static/images/name.png
    shuffle(founder_list) # random order of pics bc why not
    if (founder_list[0] == 'David'): alert_msg = "This is an error!"
    return render_template('index.html', title='Home', names=founder_list, alert_msg=alert_msg)


@app.route('/signup', methods=['POST','GET'])
def signup():
    email = request.values['email']
    name = request.values['name']
    password = request.values['password']

    user_exist = datastore.Client().query(kind = 'user')
    user_exist.add_filter('email','=', email)
    
    for user in user_exist.fetch():
        if user['email'] == email:
            return render_template('login.html')

    new_user = create_user()
    new_user['name'] = name
    new_user['email'] = email
    new_user['password'] = generate_password_hash(password, method='sha256')

    datastore.Client().put(new_user)

    return render_template('profile.html')

@app.route('/login')
@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/loginpost', methods=['POST','GET'])
def handle_request_login():
    email = request.values['email']
    password = request.values['password']

    user_exist = datastore.Client().query(kind='user')
    user_exist.add_filter('email','=',email)

    user = list(user_exist.fetch())[0]

    if not user or not check_password_hash(user['password'], password):
        return render_template('login.html')
    
    return render_template('profile.html')


@app.route('/roomieQuiz')
@app.route('/roomieQuiz.html')
def questionnaire():
    return render_template('roomieQuiz.html', title='Questionnaire')

@app.route('/DisplayQuestionnaire')
def DisplayQuestionnaire():
    try:
        name = request.values["name"]
        prsntype ="Personality Type: %s" % (request.values["type"])
        pet = "Pet Policy: %s" % (request.values["pet"])
        smoke = "Smoke Policy: %s" % (request.values["smoke"])
        friends = "Friend Policy: %s" % (request.values["friends"])
        bedtime = "Bedtime: %s" % (request.values["bedtime"])

        list = [prsntype, pet, smoke, friends, bedtime]

        return render_template('quizResults.html', title = "Results", Name = name, results = list)
    except:
        return questionnaire()
@app.route('/JoinNow')
@app.route('/JoinNow.html')
def Join():
     return render_template('JoinNow.html',title ="JoinNow")

@app.route('/emailsubmission')
def emailsubmission():
     try:
         name = request.values["name"]
         email = request.values["email"]
         return render_template('JoinSuccess.html', title = "Success", Name = name, results = email)
     except:
        return Join()


@app.route('/profiles')
@app.route('/profiles.html')
@app.route('/profile')
@app.route('/profile.html')
def showProfiles():
    query = datastore.Client().query(kind = 'user')
    users = list(query.fetch())
    return render_template('profiles.html', title="Profiles", users=users)

@app.route('/profile/<id>')
def showProfile(id):
    query = datastore.Client().query(kind = 'user')
    query.add_filter('id','=',id)
    user = list(query.fetch())
    if user:
        return render_template('profile.html', title="Profile", user=user)
    else:
        return showProfiles()

@app.errorhandler(404)
@app.route('/404.html')
@app.route('/404')
def error404(e):
    return render_template('404.html', title='404'), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
