from flask import jsonify, url_for, request, g, current_app

from . import api
from .. import db
from ..models import Post, Like, User


@api.route('/posts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['BLOGY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items

    page_prev = None
    if pagination.has_prev:
        page_prev = url_for('api.get_posts', page=page - 1)
    page_next = None
    if pagination.has_next:
        page_next = url_for('api.get_posts', page=page + 1)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': page_prev,
        'next': page_next,
        'count': pagination.total
    })


@api.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_json())


@api.route('/posts', methods=['POST'])
def new_post():
    json_post = request.json
    post = Post.from_json(json_post)
    post.author = g.current_user

    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_json()), 201


@api.route('/posts/<int:post_id>/users-like', methods=['GET'])
def get_user_like_post(post_id):
    likes = Like.query.filter(Like.post_id == post_id)
    users_like = []
    for like in likes:
        user = User.query.get(like.author_id)
        if user:
            users_like.append(user.to_json())

    return jsonify({'users_like': users_like})


@api.route('/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like()
    like.post = post
    like.author = g.current_user

    db.session.add(like)
    db.session.commit()

    return jsonify({'message': 'Like succeed'}), 201


@api.route('/posts/<int:post_id>/dislike', methods=['POST'])
def dislike_post(post_id):
    user = g.current_user
    like = Like.query \
        .filter(Like.post_id == post_id, Like.author_id == user.id).first()

    if like is not None:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'message': 'Dislike succeed'}), 200

    return jsonify({'message': 'You are not like this post'}), 400
