import facebook
import requests
from flask import jsonify, request

from . import api
from .. import db
from ..models import User


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
    if login_type is None or token is None:
        return bad_request("login_type and token is required")

    if login_type.upper() == LoginType.GOOGLE:
        google_res = requests.get(GOOGLE_OAUTH2_API_URL +
                                  "/tokeninfo?id_token=" + token)
        google_user = google_res.json()
        # Check email
        google_email = google_user.get('email', None)
        user = User.query.filter_by(email=google_email.lower()).first()
        if user:
            return conflict('An account with this email already exist')
        else:
            user = User(email=google_email, member_from=LoginType.GOOGLE)
            user.gg_id = google_user.get('sub', '')

            db.session.add(user)
            db.session.commit()
            return jsonify({
                'user': user.to_json()
            })
    elif login_type.upper() == LoginType.FACEBOOK:
        graph = facebook.GraphAPI(access_token=token, version='3.1')
        facebook_user = graph.get_object('me?fields=id,name,email')
        # Check email
        facebook_email = facebook_user.get('email', None)
        user = User.query.filter_by(email=facebook_email.lower()).first()
        if user:
            return conflict('An account with this email already exist')
        else:
            user = User(email=facebook_email, member_from=LoginType.FACEBOOK)
            user.fb_id = facebook_user.get('id', '')

            db.session.add(user)
            db.session.commit()
            return jsonify({
                'user': user.to_json()
            })
    else:
        return bad_request('Unknown login type. Must be facebook or google')


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def conflict(message):
    response = jsonify({'error': 'conflict', 'message': message})
    response.status_code = 409
    return response
