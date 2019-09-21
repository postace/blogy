import facebook
import requests
from flask import jsonify, request, g
from flask_jwt_extended import (create_access_token,
                                jwt_required,
                                get_jwt_identity)

from . import api
from .. import db
from ..models import User


class LoginType:
    FACEBOOK = 'FACEBOOK'
    GOOGLE = 'GOOGLE'


GOOGLE_OAUTH2_API_URL = 'https://oauth2.googleapis.com'


@api.before_app_request
def before_app_request():
    """ Every route except auth/login will require authentication """
    if 'auth/login' not in request.path:
        user_id = get_user_id()
        user = User.query.get(user_id)
        if not user:
            return not_found("User not found with id {}" % user_id)

        if user_not_going_to_provide_required_info(request, user):
            return bad_request("You have to provide the required info to using this feature")

        # Set global user
        g.current_user = user


@jwt_required
def get_user_id():
    return get_jwt_identity()


def user_not_going_to_provide_required_info(req, user):
    return 'me/supply-info' not in req.path \
            and not user.has_required_info


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
        google_email = google_user.get('email')
        user = User.query.filter_by(email=google_email.lower()).first()
        if user:
            return conflict('An account with this email already exist')
        else:
            user = User(email=google_email.lower(), member_from=LoginType.GOOGLE)
            user.gg_id = google_user.get('sub')

            db.session.add(user)
            db.session.commit()

            return jsonify({
                'user': user.to_json(),
                'access_token': create_access_token(identity=user.id)
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
            user = User(email=facebook_email.lower(), member_from=LoginType.FACEBOOK)
            user.fb_id = facebook_user.get('id')

            db.session.add(user)
            db.session.commit()
            return jsonify({
                'user': user.to_json(),
                'access_token': create_access_token(identity=user.id)
            })
    else:
        return bad_request('Unknown login type. Must be facebook or google')


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def not_found(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 404
    return response


def conflict(message):
    response = jsonify({'error': 'conflict', 'message': message})
    response.status_code = 409
    return response
