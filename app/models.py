from datetime import datetime

from . import db
from app.exceptions import ValidationError


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String(32), unique=True, index=True)
    gg_id = db.Column(db.String(32), unique=True, index=True)
    email = db.Column(db.String(256), unique=True, index=True, nullable=False)
    name = db.Column(db.String(64))
    phone_number = db.Column(db.String(16))
    occupation = db.Column(db.String(64))
    member_from = db.Column(db.String(16))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow())
    has_required_info = db.Column(db.Boolean, default=False, nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='author', lazy='dynamic')

    def to_json(self):
        json_user = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'member_since': self.member_since,
            'has_required_info': self.has_required_info
        }
        return json_user


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    likes = db.relationship('Like', backref='post', lazy='dynamic')

    def to_json(self):
        json_post = {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'timestamp': self.timestamp,
            'author_id': self.author_id
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        title = json_post.get('title')
        content = json_post.get('content')
        if title is None or title == '' \
                or content is None or content == '':
            raise ValidationError('title and content is required for post')
        return Post(title=title, content=content)


class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

    def to_json(self):
        json_like = {
            'author_id': self.author_id,
            'post_id': self.post_id
        }
        return json_like
