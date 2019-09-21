import unittest
from app import create_app, db
from app.models import User, Post
from flask_jwt_extended import create_access_token
from faker import Faker
from sqlalchemy.exc import IntegrityError
from random import randint
import json


def build_api_headers(user_id: int):
    jwt_token = create_access_token(identity=user_id)
    return {
        'Authorization':
            'Bearer ' + jwt_token,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }


def add_user_bob():
    user_bob = User(email='bob@gmail.com', member_from='GOOGLE')
    user_bob.has_required_info = True
    db.session.add(user_bob)
    db.session.commit()
    return user_bob


def fake_create_user(count=10):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 name=fake.name(),
                 has_required_info=True,
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def fake_create_post(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(title=fake.name(),
                 content=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()


class PostAPITestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client(use_cookies=False)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_new_post(self):
        user_bob = add_user_bob()

        # Write a post
        response = self.client.post(
            '/api/posts',
            headers=build_api_headers(user_bob.id),
            data=json.dumps({'title': 'post 1', 'content': 'Simple content'}))
        self.assertEqual(response.status_code, 201)
        json_response = response.get_json()
        self.assertEqual(json_response.get('title'), 'post 1')
        self.assertEqual(json_response.get('content'), 'Simple content')
        self.assertEqual(json_response.get('author_id'), user_bob.id)
        self.assertEqual(json_response.get('like_label'), None)

    def test_get_posts(self):
        fake_create_user(count=10)
        fake_create_post(count=50)

        user_bob = add_user_bob()
        response = self.client.get(
            '/api/posts',
            headers=build_api_headers(user_bob.id))

        self.assertEqual(response.status_code, 200)
        json_response = response.get_json()
        self.assertEqual(json_response.get('count'), 50)
        self.assertIsNotNone(json_response.get('next'))




if __name__ == '__main__':
    unittest.main()
