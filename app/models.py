from datetime import datetime

from . import db


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

    def to_json(self):
        json_user = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'member_since': self.member_since,
            'has_enough_info': self.has_required_info
        }
        return json_user
