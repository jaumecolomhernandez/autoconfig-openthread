import sys
import os
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    from tcp_customserver import TEST  # Avoiding circular dependencies problem, replace by PAEManager
    print(TEST)
    return "Hello, World!"
