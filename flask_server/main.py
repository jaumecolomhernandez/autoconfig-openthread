import sys
import os
from flask import Flask, render_template, request, Response, abort, redirect
from flask_login import LoginManager, UserMixin, \
                                login_required, login_user, logout_user 
#from .login import login_manager

app = Flask(__name__)

app.config.update(
    SECRET_KEY = 'test'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "user" + str(id)
        self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)

#TODO: USE DB

users = [User(id) for id in range(0, 20)]

# somewhere to login
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

# handle login failed
@app.errorhandler(401)
def page_not_found(e):
	#TODO: RETURN A HTML
    return Response('<p>Login failed</p>')

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
	#TODO: RETURN A HTML
    return Response('<p>Logged out</p>')


@login_manager.user_loader
def load_user(userid):
    return User(userid)


@app.route("/")
@login_required
def home():
	from tcp_customserver import TEST
	print(TEST)
	return render_template('button.html')


@app.route("/button1", methods=['GET', 'POST'])
@login_required
def button_handler():
	print("Update")
	return render_template('button.html', test="bye")




#if __name__ == "__main__":
#	app.run(debug=True)