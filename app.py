"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from flask import Flask, render_template, request, redirect, url_for

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

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
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
###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
