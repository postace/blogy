from flask import jsonify, request, g

from . import api
from .. import db
from ..models import Post


@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


@api.route('/posts', methods=['POST'])
def new_post():
    json_post = request.json
    post = Post.from_json(json_post)
    post.author = g.current_user

    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_json()), 201
