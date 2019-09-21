from flask import jsonify, request, g, current_app, url_for

from . import api
from .authentication import LoginType, bad_request
from .. import db
from ..models import Post


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


@api.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    user = g.current_user
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items

    page_prev = None
    if pagination.has_prev:
        page_prev = url_for('api.get_user_posts', id=user_id, page=page - 1)
    page_next = None
    if pagination.has_next:
        page_next = url_for('api.get_user_posts', id=user_id, page=page + 1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': page_prev,
        'next': page_next,
        'count': pagination.total
    })
