from flask import Flask, render_template, request, Response, abort, redirect, Blueprint 

errors_bp = Blueprint('errors', __name__, template_folder='templates')                                

# handle login failed
@errors_bp.app_errorhandler(401)
def login_failed(e):
	#TODO: RETURN A HTML
    return Response('<p>Login failed</p>')

# handle login failed
@errors_bp.app_errorhandler(404)
def not_found(e):
	#TODO: RETURN A HTML
    return render_template('404.html')