from flask import jsonify, request, g

from . import api
from .. import db
from ..models import Post


@api.route('/posts', methods=['POST'])
def new_post():
    json_post = request.json
    post = Post.from_json(json_post)
    post.author = g.current_user

    db.session.add(post)
    db.session.commit()

    return jsonify(post.to_json()), 201
