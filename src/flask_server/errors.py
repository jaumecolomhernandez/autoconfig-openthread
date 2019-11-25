from flask import Flask, render_template, request, Response, abort, redirect, Blueprint
import logging

logger = logging.getLogger('flask_server')
errors_bp = Blueprint('errors', __name__, template_folder='templates')                                


# handle login failed
@errors_bp.app_errorhandler(401)
def login_failed(e):
	logger.info(f'AUTH Failed! Wrong Username or PW')
	return render_template('login.html', err="Wrong user/pw combination. Try again!")


# handle page doesn't exist
@errors_bp.app_errorhandler(404)
def not_found(e):
	return render_template('404.html')