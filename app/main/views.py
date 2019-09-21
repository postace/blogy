from flask import render_template
from . import main


@main.route('/google-login', methods=['GET'])
def login_with_google():
    return render_template('google_login.html')


@main.route('/facebook-login', methods=['GET'])
def login_with_facebook():
    return render_template('facebook-login.html')
