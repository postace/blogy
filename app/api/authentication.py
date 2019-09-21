import facebook
import requests
from flask import jsonify, request, g
from flask_jwt_extended import (create_access_token,
                                jwt_required,
                                get_jwt_identity)

from . import api
from .errors import not_found, bad_request, conflict, unauthorized
from .. import db
from ..models import User


class LoginType:
    FACEBOOK = 'FACEBOOK'
    GOOGLE = 'GOOGLE'


GOOGLE_OAUTH2_API_URL = 'https://oauth2.googleapis.com'


@api.before_request
def before_request():
    """ Every route except auth/login will require authentication """
    if 'auth/login' not in request.path:
        user_id = get_user_id()
        user = User.query.get(user_id)
        if not user:
            return not_found("User not found with id {}".format(user_id))

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
        gg_user = google_res.json()
        return new_user_with_type(gg_user.get('email'),
                                  LoginType.GOOGLE,
                                  gg_user.get('sub'))
    elif login_type.upper() == LoginType.FACEBOOK:
        graph = facebook.GraphAPI(access_token=token, version='3.1')
        fb_user = graph.get_object('me?fields=id,name,email')

        return new_user_with_type(fb_user.get('email'),
                                  LoginType.FACEBOOK,
                                  fb_user.get('id'))
    else:
        return bad_request('Unknown login type. Must be facebook or google')


def new_user_with_type(email, login_from, third_party_id):
    if email is None or email == '':
        return unauthorized('Error when login {}'.format(login_from))
    user = User.query.filter_by(email=email.lower()).first()
    if user:
        return conflict('An account with email {} already exist'.format(email))

    user = User(email=email.lower(), member_from=login_from)
    if login_from == LoginType.FACEBOOK:
        user.fb_id = third_party_id
    elif login_from == LoginType.GOOGLE:
        user.gg_id = third_party_id

    db.session.add(user)
    db.session.commit()
    return jsonify({
        'user': user.to_json(),
        'access_token': create_access_token(identity=user.id)
    })
