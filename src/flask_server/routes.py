from flask import Flask, render_template, Blueprint, current_app, request
from flask_login import login_required, current_user

routes_bp = Blueprint('routes', __name__, template_folder='templates')
# TODO: Create complete UI using Bootstrap and Jquery

@routes_bp.route("/")
@login_required
def home():
	return render_template('index.html', devices=current_app.manager.devices, user=current_user)


@routes_bp.route("/send", methods=['GET', 'POST'])
@login_required
def send_cmd():
	print(f"id {request.form['id']} : {request.form['command']}")
	return render_template('index.html', devices=current_app.manager.devices, user=current_user)


@routes_bp.route("/button1", methods=['GET', 'POST'])
@login_required
def button_handler():
	print("Update")
	return render_template('button.html', test="bye")