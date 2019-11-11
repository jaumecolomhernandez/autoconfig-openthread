import sys
import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
   # from tcp_customserver import TEST  # Avoiding circular dependencies problem, replace by PAEManager
   #print(TEST)
    return render_template('button.html', test="hello")


@app.route("/button1", methods=['GET', 'POST'])
def button_handler():
	print("Update")
	return render_template('button.html', test="bye")

#if __name__ == "__main__":
#	app.run(debug=True)