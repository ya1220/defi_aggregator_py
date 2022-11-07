from config import engine
from auth import (
    User,
    PasswordChange,
    add_user,
    change_user,
    del_user,
    show_users,
    user_exists
)

# engine is open to sqlite///users.db

# add a test user to the database
email = 'ya1220@gmail.com'
del_user(email,engine)

show_users(engine) # show that the users exists
print(user_exists(email,engine)) # confirm that user exists


