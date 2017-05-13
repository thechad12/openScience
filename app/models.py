from flask import Flask, render_template, request
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
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

class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), unique=True)
	first_name = db.Column(db.String(120))
	last_name = db.Column(db.String(120))
	posts = db.relationship('Post', backref='author', lazy='dynamic')

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

class Post(db.Model):
	__tablename__ = 'post'
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(2000))
	title = db.Column(db.String(250))
	timestamp = db.Column(db.DateTime)
	user_id = Column(db.Integer, db.ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		return {
			'title': self.title,
			'id': self.id,
			'user_id': self.user_id,
			'text': self.text
		}