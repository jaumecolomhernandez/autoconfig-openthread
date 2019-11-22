from flask import Flask, render_template, Blueprint, current_app, request
from flask_login import login_required, current_user
import logging

routes_bp = Blueprint('routes', __name__, template_folder='templates')
log = logging.getLogger('flask_routes')
# TODO: Create complete UI using Bootstrap and Jquery

@routes_bp.route("/")
@login_required
def home():
	return render_template('index.html', devices=current_app.manager.devices, user=current_user)


@routes_bp.route("/send", methods=['GET', 'POST'])
@login_required
def send_cmd():
	#print(f"id {request.form['id']} : {request.form['command']}")
	# TODO: Show some message in the UI confirming the sending of the message
	# TODO: Show pseudoCLI to see the response
	current_app.manager.get_device(id_number=int(request.form['id'])).send_command(request.form['command'])
	log.info(f"Sent message: '{request.form['command']}' to device with id: {request.form['id']}")
	return render_template('index.html', devices=current_app.manager.devices, user=current_user)


@routes_bp.route("/button1", methods=['GET', 'POST'])
@login_required
def button_handler():
	print("Update")
	return render_template('button.html', test="bye")