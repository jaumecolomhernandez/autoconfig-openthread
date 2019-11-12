import sys
import os
from flask import Flask, render_template, request, Response, abort, redirect
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user 
from .errors import errors_bp
from .routes import routes_bp
from .models import User

app = Flask(__name__)

app.config.update(
    SECRET_KEY = 'test'
)
# Add blueprints, routes from other files
app.register_blueprint(errors_bp)
app.register_blueprint(routes_bp)


# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']        
		if password == username + "_secret":
			id = username.split('user')[1]
			user = User(id)
			login_user(user)
			return redirect(request.args.get("next"))
		else:
			return abort(401)
	else:
		#TODO: RETURN A HTML
		return Response('''
	    <form action="" method="post">
	        <p><input type=text name=username>
	        <p><input type=password name=password>
	        <p><input type=submit value=Login>
	    </form>
	    ''')

@app.route("/logout")
@login_required
def logout():
    logout_user()
	#TODO: RETURN A HTML
    return Response('<p>Logged out</p>')

@login_manager.user_loader
def load_user(userid):
    return User(userid)