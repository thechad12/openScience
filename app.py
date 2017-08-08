import os
from flask import Flask, render_template, request, redirect, url_for
from models import FacebookSignIn, OAuthSignIn, User, Post
import json
import requests
import random
import string
from oauth2client.client import flow_from_clientsecrets, OAuth2WebServerFlow, FlowExchangeError


app = Flask(__name__)

facebook_id = json.loads(open('facebook.json','r')
    .read())['web']['client_id']
facebook_secret = json.loads(open('facebook.json','r')
    .read())['web']['secret_key']

google_id = json.loads(open('google.json','r')
    .read())['web']['client_id']
google_secret = json.loads(open('google.json','r')
    .read())['web']['secret_key']

APPLICATION_NAME = 'open cosmos'

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')
app.config['OAUTH_CREDENTIALS'] = {
    'facebook': {
        'id': facebook_id,
        'secret': facebook_secret
    },
    'google': {
        'id': google_id,
        'secret': google_secret
    }
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/user/<email>')
def user(email):
    user = User.query.filter_by(email=email).first()
    if user == None:
        flash('User %s not found.' % email)
        return redirect(url_for('home'))
    return render_template('user.html',
                            user=user,
                            posts=posts)

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, first_name, last_name = oauth.callback()
    if social_id is None:
        flash('Authentication failed')
        return redirect(url_for('home'))
    user = User.query(filter_by(social_id))
    if not user:
        user = User(id=social_id,email=email,first_name=first_name,
            last_name=last_name)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('home'))

@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/logout')
def logout():
    session.delete(login_session)
    session.commit()
    flash("You have successfully been logged out")
    return render_template('home.html')

def create_user(login_session):
    newUser = User(first_name=login_session['first_name'],
        last_name=login_session['last_name'], email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()

@app.route('/follow/<email>')
def follow(email):
    user = User.query.filter_by(email=email).first()
    if user is None:
        flash('User %s not found.' % email)
        return redirect(url_for('home'))
    u = user.follow(user)
    if u is None:
        return redirect(url_for('home'))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + email + '!')
    return redirect(url_for('home'))

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
