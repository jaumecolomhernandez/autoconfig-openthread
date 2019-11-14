from flask import Flask, render_template, Blueprint
from flask_login import login_required

routes_bp = Blueprint('routes', __name__, template_folder='templates')
# TODO: Create complete UI using Bootstrap and Jquery

@routes_bp.route("/")
@login_required
def home():
	from tcp_customserver import TEST
	print(TEST)
	return render_template('button.html')


@routes_bp.route("/button1", methods=['GET', 'POST'])
@login_required
def button_handler():
	print("Update")
	return render_template('button.html', test="bye")
