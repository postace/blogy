from flask import jsonify, request
import requests
from ..models import User
from .. import db
from . import api


@api.before_request
def before_request():
    # Check if route is /auth/login then we do not need to validate them
    # Otherwise, check if user does not have enough information and return err
    print("Incoming request path ", request.path)


class LoginType:
    FACEBOOK = 'FACEBOOK'
    GOOGLE = 'GOOGLE'


GOOGLE_OAUTH2_API_URL = 'https://oauth2.googleapis.com'


@api.route('/auth/login', methods=['POST'])
def login_or_register():
    req_body = request.json
    login_type = req_body.get('login_type')
    token = req_body.get('token')

    if login_type.upper() == LoginType.GOOGLE:
        google_res = requests.get(GOOGLE_OAUTH2_API_URL +
                                  "/tokeninfo?id_token=" + token)
        google_user = google_res.json()
        # Check email
        google_email = google_user.get('email', '')
        user = User.query.filter_by(email=google_email.lower()).first()
        if user:
            return jsonify({'message': 'User with this email already exist'})
        else:
            # Save user to database
            user = User(email=google_email)
            db.session.add(user)
            db.session.commit()
            return jsonify({'user': user.to_json()})

    return jsonify({'message': 'ok'})
