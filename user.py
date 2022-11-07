from auth import pwdb, User as base
from flask_login import login_user, logout_user, current_user, LoginManager, UserMixin

# Create User class with UserMixin
class User(UserMixin, base):
    pass

