from flask import jsonify, request
from . import api


@api.before_request
def before_request():
    # Check if route is /auth/login then we do not need to validate them
    # Otherwise, check if user does not have enough information and return err
    print("Incoming request path ", request.path)


@api.route('/auth/login', methods=['POST'])
def login_or_register():
    # Several job to be done here
    # Check type is facebook/google
    # Make an api request to two of these
    # Received data back
    # Check email
    # If exists -> then create token and return along with user information
    # Otherwise -> create user, create token and return information
    return jsonify({'message': 'ok'})
