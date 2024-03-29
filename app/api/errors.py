from flask import jsonify
from app.exceptions import ValidationError, OAuthTokenError
from . import api


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def not_found(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 404
    return response


def conflict(message):
    response = jsonify({'error': 'conflict', 'message': message})
    response.status_code = 409
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@api.errorhandler(OAuthTokenError)
def oauth_token_error(e):
    return unauthorized(e.args[0])
