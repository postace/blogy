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

GOOGLE_OAUTH2_API_URL = 'https://oauth2.googleapis.com'


class LoginType:
    FACEBOOK = 'FACEBOOK'
    GOOGLE = 'GOOGLE'

    @staticmethod
    def is_unknown(type_to_check: str):
        return type_to_check is not None and \
               type_to_check.upper() != LoginType.GOOGLE and \
               type_to_check.upper() != LoginType.FACEBOOK


class SocialUser:
    def __init__(self, email, id, login_from):
        self.email = email
        self.id = id
        self.login_from = login_from


@api.before_request
def before_request():
    """ Every route except auth/login will require authentication """
    if 'auth/login' not in request.path:
        user_id = get_user_id()
        user = User.query.get(user_id)
        if not user:
            return not_found("User not found with id {}".format(user_id))

        if user_not_going_to_provide_required_info(request, user):
            return bad_request("Please supply the required info at API: "
                               "/api/me/supply-info before using this feature")

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
    if token is None:
        return bad_request("Token is required")
    if LoginType.is_unknown(login_type):
        return bad_request('Unknown login type. Must be facebook or google')

    social_user = fetch_social_user(login_type, token)
    if social_user.email is None or social_user.email == '':
        return unauthorized('Email not found when login {}'
                            .format(social_user.login_from))
    user = User.query.filter_by(email=social_user.email.lower()).first()

    if exist_user_login(user, login_type.upper()):
        return jsonify({
            'user': user.to_json(),
            'access_token': create_access_token(identity=user.id)})
    if same_email_login_from_other_source(user, login_type.upper()):
        return conflict('An account with email {} already exist'.format(social_user.email))

    user = save_new_user(social_user)
    return jsonify({
        'user': user.to_json(),
        'access_token': create_access_token(identity=user.id)})


def fetch_social_user(login_type, token):
    social_user = SocialUser(None, None, None)
    if login_type.upper() == LoginType.GOOGLE:
        google_res = requests.get(GOOGLE_OAUTH2_API_URL +
                                  "/tokeninfo?id_token=" + token)
        gg_user = google_res.json()
        social_user = SocialUser(
            gg_user.get('email'), gg_user.get('sub'), LoginType.GOOGLE)
    elif login_type.upper() == LoginType.FACEBOOK:
        graph = facebook.GraphAPI(access_token=token, version='3.1')
        fb_user = graph.get_object('me?fields=id,name,email')
        social_user = SocialUser(
            fb_user.get('email'), fb_user.get('id'), LoginType.FACEBOOK)

    return social_user


def exist_user_login(user: User, login_from: str) -> bool:
    return user and user.member_from == login_from


def same_email_login_from_other_source(user: User, login_from: str) -> bool:
    return user and user.member_from != login_from


def save_new_user(social_user: SocialUser) -> User:
    user = User(email=social_user.email.lower(),
                member_from=social_user.login_from.upper())

    if social_user.login_from == LoginType.FACEBOOK:
        user.fb_id = social_user.id
    elif social_user.login_from == LoginType.GOOGLE:
        user.gg_id = social_user.id
    db.session.add(user)
    db.session.commit()
    return user
