from flask import Flask
from flask_login import LoginManager, UserMixin, login_required

class User(UserMixin):
    def __init__(self, user):
        self.id = str(user)
        self.name = self.id
        self.password = ""
        
    def __repr__(self):
        return "%s" % self.name



