from flask import jsonify, request
import facebook
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
    # Check login_type
    # Check token

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
    elif login_type.upper() == LoginType.FACEBOOK:

        graph = facebook.GraphAPI(access_token=token, version='3.1')
        facebook_user = graph.get_object('me?fields=id,name,email')
        # Check email
        facebook_email = facebook_user.get('email', '')
        user = User.query.filter_by(email=facebook_email.lower()).first()
        if user:
            return jsonify({'message': 'User with this email already exist'})
        else:
            # Save user to database
            user = User(email=facebook_email)
            db.session.add(user)
            db.session.commit()
            return jsonify({'user': user.to_json()})


    # Throw error here because login-type is not defined
    return jsonify({'message': 'ok'})
