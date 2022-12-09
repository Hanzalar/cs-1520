from flask import Flask
from flask import Response
from flask import request
from flask import render_template
from flask import flash
from flask import session
from random import shuffle
from werkzeug.security import generate_password_hash, check_password_hash
from google.cloud import datastore
from google.cloud import storage
from google.cloud import secretmanager

app = Flask(__name__)

BUCKET_NAME = "grouph-bucket"



def get_secret_key():
    ''' pull flask secret key from google secret manager, not in plaintext! '''
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Access the secret version.
    response = client.access_secret_version(name='projects/370368880243/secrets/flask-secret-key/versions/1')

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')

app.secret_key = get_secret_key() # so we can have session cookies


NAVBAR_AUTH = [
    ["/profile.html", "fa-user-circle-o", "My Profile"],
    ["/logout.html", "fa-user-circle-o", "Log Out"],
    ["/editprofile.html", "fa-pencil-square-o", "Edit Profile"],
    ["/roomateTinder.html", "fa-search-plus", "Find A Match"]
    ["/profiles.html", "fa-search-plus", "Show Match"]
]

NAVBAR_NOAUTH = [
    ["/index.html#team", "fa-sitemap", "Team"],
    ["/JoinNow.html", "fa-user-plus", "Join Now"],
    ["/login.html", "fa-user-circle-o", "Log In"],
    ["/index.html#contact", "fa-envelope-o", "Contact"]
]

def create_user():
    client = datastore.Client()

    key = client.key('testuser')

    return datastore.Entity(key)

def get_user(): # for session checks
    return session.get('user', None)

def get_Suitors(): # for getting list of elegible bacelor/bachloretes
    user = load_user(session['user'])
    intersect =user['yes'] + user['no'] + user['matched']
    query = datastore.Client().query(kind = 'testuser')
    currentusers=list(query.fetch())
    users = [i for i in currentusers if i not in intersect]
    return  users

def load_user(id=None, email=None):
    query = datastore.Client().query(kind = 'testuser')
    if email:
        query.add_filter('email','=',email)
    elif id:
        key = datastore.Client().key('testuser',id)
        query.key_filter(key)

    for user in query.fetch():
        return user
    return None

def get_matches(): # for getting list of matches
    user = load_user(session['user'])
    match = user['matched']
    return match


@app.route('/')
@app.route('/index.html')
@app.route('/default.html')
def root():
    if get_user(): # if you're logged in go back to profiles
        return show_profiles()
    else: # show regular home page
        founder_list = [
            'Hanzala',
            'David',
            'Derrick',
            'Erasto'
        ] # this assumes that for name there is an image file at /static/images/name.png
        shuffle(founder_list) # random order of pics bc why not
        return render_template('index.html', title='Home', names=founder_list, success='Alerts work now!', nav=NAVBAR_NOAUTH)


@app.route('/signup', methods=['POST'])
def dosignup():
    email = request.values['email']
    name = request.values['name']
    locationzip = request.values['locationzip']
    age = request.values['age']
    password = request.values['password']
    bio = request.values['bio']
    user_exist = datastore.Client().query(kind = 'testuser')
    user_exist.add_filter('email','=', email)
    
    for user in user_exist.fetch():
        if user['email'] == email:
            return render_template('/login.html')

    new_user = create_user()
    new_user['name'] = name
    new_user['email'] = email
    new_user['locationzip']=locationzip
    new_user['age'] = age
    new_user['bio'] = bio
    new_user['password'] = generate_password_hash(password, method='sha256')
    new_user['picture'] = '/static/images/blank-user.png'
    new_user['picinc'] = 0
    new_user['yes'] = list()
    new_user['no'] = [new_user.key.id]
    new_user['matched'] = list()

    datastore.Client().put(new_user)

    session['user'] = new_user.key.id

    return render_template('profile.html', user = new_user, nav=NAVBAR_AUTH)

@app.route('/login')
@app.route('/login.html')
def login():
    if get_user(): # if you're logged in go back to profiles
        return show_profiles()
    else:
        return render_template('login.html', nav=NAVBAR_NOAUTH)

@app.route('/loginpost', methods=['POST'])
def dologin():
    email = request.values['email']
    password = request.values['password']

    user = load_user(email=email)

    if user and check_password_hash(user['password'], password):
        ''' add user to session '''
        session['user'] = user.key.id
        session["count"]=0
        return render_template('profile.html', user = user, nav=NAVBAR_AUTH)
    
    return render_template('login.html', nav=NAVBAR_NOAUTH)

@app.route('/logout')
@app.route('/logout.html')
def logout():
    session['user'] = None
    return root()


@app.route('/editprofile')
@app.route('/editprofile.html')
def editprofile():
    user = load_user(id=session['user'])
    return render_template('editprofile.html', user = user, nav =NAVBAR_AUTH)

@app.route('/saveprofile', methods=["POST"])
def saveprofile():
    id = session['user']
    user = load_user(id=id)
    user['name'] = request.values['name']
    user['age'] = request.values['age']
    file = request.files.get('picture')
    user['bio'] = request.values['bio']   
    bucket = storage.Client().get_bucket(BUCKET_NAME)
    blob = bucket.blob(str(id))
    c_type = file.content_type
    blob.upload_from_string(file.read(), content_type = c_type)
    user['picture'] = blob.public_url
    user['picinc'] += 1
    datastore.Client().put(user)    
    return render_template('profile.html', user = user, nav = NAVBAR_AUTH)

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
    if get_user(): # if you're logged in go back to profiles
        return show_profiles()
    else: 
        return render_template('JoinNow.html',title ="JoinNow", nav=NAVBAR_NOAUTH)

@app.route('/emailsubmission')
def emailsubmission():
     try:
         name = request.values["name"]
         email = request.values["email"]
         return render_template('JoinSuccess.html', title = "Success", Name = name, results = email, nav=NAVBAR_NOAUTH)
     except:
        return Join()

@app.route('/profiles')
@app.route('/profiles.html')
def show_profiles():
    if get_user():
        users = get_matches()
        return render_template('profiles.html', title="Profiles", users=users, nav=NAVBAR_AUTH)
    else:
        return login()

@app.route('/profile', methods=['GET'])
@app.route('/profile.html', methods=['GET'])
def show_profile():
    if get_user():
        id = request.args.get('user') if request.args.get('user') else session['user']
        user = load_user(id=int(id))
        if user:
            return render_template('profile.html', title="Profile", user=user, nav=NAVBAR_AUTH)
        else: #if user does not exist dump back to all profiles
            return show_profiles()
        '''
        user = loaduser(session['user'])
        intersect =user['yes'] + user['no'] + user['matched']
        query = datastore.Client().query(kind = 'user')
        users = list(query.fetch())
        users = list(lambda users: (user not in intersect))
        session['count']=0
        userViewingnow = users[0] 
        return render_template('roomateTinder.html', title="Matching", user = userViewingnow.email, nav=NAVBAR_AUTH) '''
    else:
        return login()


@app.route('/roomateTinder.html')
def roomateTinder():
    if get_user():
        potRoom = get_Suitors()   
        if session["count"] <= len(potRoom) - 1:
            userViewingnow=potRoom[session["count"]]
            return render_template('roomateTinder.html', title="Matching", user = userViewingnow, nav=NAVBAR_AUTH )
        else:
            return show_profiles()
        
    else:
        return login()

@app.route('/match', methods=['POST'])
def match():
   print(request.values['match'])
   session["count"]+=1
   curruser = load_user(session['user'])
   if request.values['match'] == "accept":
        curruser['yes'].append((request.values['user']))
   if request.values['match'] == "reject":
        curruser['no'].append((request.values['user']))

   datastore.Client().put(curruser)
   return roomateTinder()

@app.errorhandler(404)
@app.route('/404.html')
@app.route('/404')
def error404(e):
    nav = NAVBAR_AUTH if get_user() else NAVBAR_NOAUTH
    return render_template('404.html', title='404', nav=nav), 404

@app.route('/sanitize', methods=['GET'])
def sanitize():
    ''' hidden function to fill db entries o_o '''

    # get secret key
    client = secretmanager.SecretManagerServiceClient()

    # Access the secret version.
    response = client.access_secret_version(name='projects/370368880243/secrets/sanitize/versions/1')

    # Return the decoded payload.
    secret = response.payload.data.decode('UTF-8')

    if secret == request.args.get('s'):
        query = datastore.Client().query(kind = 'testuser')
        users = list(query.fetch())
        for user in users:
            user['no'] = [int(user.key.id)]
            datastore.Client().put(user)

    return root()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
