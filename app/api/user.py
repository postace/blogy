from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api
from .. import db
from .authentication import LoginType, bad_request
from ..models import User


@api.route('/me/supply-info', methods=['POST'])
@jwt_required
def supply_required_info():
    req_body = request.json
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return not_found('User not found with id' % user_id)
    if user.has_required_info:
        return jsonify({'message': 'You already provide required info'})
    if not user.member_from:
        return bad_request('Unknown login type')

    if user.member_from == LoginType.GOOGLE:
        name = req_body.get('name')
        occupation = req_body.get('occupation')
        if name is None or occupation is None:
            return bad_request('Name or occupation is required')

        user.name = name
        user.occupation = occupation
    elif user.member_from == LoginType.FACEBOOK:
        phone_number = req_body.get('phone_number')
        name = req_body.get('name')
        if name is None or phone_number is None:
            return bad_request('Name and phone number is required')

        user.phone_number = phone_number
        user.name = name

    user.has_required_info = True
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Supply information succeed', 'user': user.to_json()})


def not_found(message):
    response = jsonify({'error': 'not found', 'message': message})
    response.status_code = 404
    return response
