import sys
import os
from flask import Flask, render_template, request, Response, abort, redirect, g
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user 
from .errors import errors_bp
from .routes import routes_bp
from .api import api_bp
from .models import User

app = Flask(__name__)

app.config.update(
    SECRET_KEY = 'test'
)
# Add blueprints, routes from other files
app.register_blueprint(errors_bp)
app.register_blueprint(routes_bp)
app.register_blueprint(api_bp)


# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


def init_app_old(manager, log):
	""" MANERA SUPERCUTRE DE PASSAR-LI UN OBJECTE A L'APLICACIO
		S'ha de crear una classe per a passar-li l'objecte bé,
		en cas que una classe no és pugui, mirar patrons de disseny que
		permetin fer aixo (estic segur que no som els primers ens trobar-nos
		amb aquesta barrera)
	"""
	app.manager = manager
	app.log = log
	app.test = "testing"


def init_app(manager, log):
	""" MANERA NO TAN CUTRE DE PASSAR-LI UN OBJECTE A L'APLICACIO PERO QUE NO FUNCIONA! MIRAR APP_CONTEXT
		No se si es la manera correcta de fer aixo, però pel que 
		sembla Flask te el objecte g per a (potser) resoldre aquest problema
	"""
	g.manager = manager
	g.log = log
	g.test = "this is a test"


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
			return render_template('login.html', err="Wrong user/pw combination. Try again!")
	else:
		return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
	#TODO: RETURN A HTML
    return Response('<p>Logged out</p>')

@login_manager.user_loader
def load_user(userid):
    return User(userid)