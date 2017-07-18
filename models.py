from flask import Flask, render_template, request
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from flask.ext.login import LoginManager, UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
import sys
import os
from app import db

WHOOSH_ENABLED = os.environ.get('HEROKU') is None
enable_search = WHOOSH_ENABLED
if enable_search:
	import flask_whooshalchemy as whooshalcemy
if enable_search:
	whooshalcemy.whoosh_index(app, Post)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/cosmos'
db = SQLAlchemy(app)
lm = LoginManager(app)

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), unique=True)
	first_name = db.Column(db.String(120))
	last_name = db.Column(db.String(120))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	followed = db.relationship('User',
								secondary=followers,
								primaryjoin=(followers.c.follower_id == id),
								secondaryjoin=(followers.c.followed_id == id),
								backref=db.backref('followers',lazy='dynamic'),
								lazy=dynamic)

	def __init__(self,email):
		self.email = email

	def __repr__(self):
		return '<User %r>' % (self.first_name)
	@property
	def serialize(self):
		return {
		'id': self.user_id,
		'email': self.email,
		'posts': self.posts
		}

	@lm.user_loader
	def load_user(id):
		return User.query.get(int(id))

	@property
	def is_authenticated(self):
	    return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return True

	def get_id(self):
		try:
			return unicode(self.id) # Python 2
		except NameError:
			return str(self.id)		# Python 3

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
			return self

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
			return self

	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
			followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

class Post(db.Model):
	__tablename__ = 'post'
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(2000))
	title = db.Column(db.String(250))
	timestamp = db.Column(db.DateTime)
	user_id = Column(db.Integer, db.ForeignKey('user.id'))
	user = relationship(User)
	likes = db.relationship('User',
							secondary=likes,
							primaryjoin=(likes.c.like_id == id),
							secondaryjoin=(likes.c.liked_id == id),
							backref=db.backref('likes', lazy='dynamic'),
							lazy='dynamic')

	@property
	def serialize(self):
		return {
			'title': self.title,
			'id': self.id,
			'user_id': self.user_id,
			'text': self.text
		}

	def like(self, post):
		if not self.is_liked(post):
			self.liked.append(post)
			return self

	def unlike(self, post):
		if self.is_liked(post):
			self.liked.remove(post)
			return self

	def is_liked(self, post):
		return self.liked.filter(likes.c.liked_id == post.id).count() > 0


class OAuthSignIn(object):
	providers = None

	def __init__(self, provider_name):
		self.provider_name = provider_name
		credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
		self.consumer_id = credentials['id']
		self.consumer_secret = credentials['secret']


	def authorize(self):
		pass

	def callback(self):
		pass

	def get_callback(self):
		return url_for('oauth_callback', provider=self.provider_name,
			_external=True)

	@classmethod
	def get_provider(self, provider_name):
		if self.providers is None:
			self.providers = {}
			for provider_subclass in self.__subclasses__():
				provider = provider_class()
				self.providers[providdr.provider_name] = provider
		return self.providers[provider_name]

class FacebookSignIn(OAuthSignIn):
	def __init__(self):
		super(FacebookSignIn, self).__init__('facebook')
		self.service = OAuth2Service(
			name='facebook',
			client_id=self.consumer_id,
			client_secret=self.consumer_secret,
			authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/')

	def authorize(self):
		return redirect(self.service.get_authorize_url,
			scope='email',
			response_type='code',
			redirect_uri=self.get_callback_url()
			)

	def callback(self):
		def decode_json(payload):
			return json.loads(payload.decode('utf-8'))

		if 'code' not in request.args:
			return None, None, None
		oauth_session = self.service.get_auth_session(
			data={'code':request.args['code'],
				'grant_type': 'authorization_code',
				'redirect_uri': self.get_callback_url()},
				decoder=decode_json
				)
		me = oauth_session.get('me').json()
		return(
			'facebook$' + me['id'],
			me.get('email').split('@')[0],
			me.get('email')
			)

followers = db.Table('followers',
	db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
	db.Column('followed_id',db.Integer,db.ForeignKey('user.id'))
	)

likes = db.Table('likes',
	db.Column('like_id',db.Integer,db.ForeignKey('user.id')),
	db.Column('liked_id',db.Integer,db.ForeignKey('post.id'))
	)
