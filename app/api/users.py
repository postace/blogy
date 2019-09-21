from flask import jsonify, request, g

from . import api
from .. import db
from .authentication import LoginType, bad_request


@api.route('/me/supply-info', methods=['POST'])
def supply_required_info():
    req_body = request.json
    user = g.current_user

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

