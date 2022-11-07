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

def create_user_table(model,engine):
    model.metadata.create_all(engine)

def create_password_change_table(model,engine):
    model.metadata.create_all(engine)

create_user_table(User,engine)
create_password_change_table(PasswordChange,engine)

# add a test user to the database
first = 'erik'
last = 'liechtenstein'
email = 'anagamicapital@gmail.com'
password = 'stablecoinyieldishigh'
add_user(first,last,password,email,engine)

show_users(engine) # show that the users exists
print(user_exists(email,engine)) # confirm that user exists


