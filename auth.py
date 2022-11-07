import traceback
from sqlalchemy import Table, create_engine, MetaData
from sqlalchemy.sql import select, and_
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from werkzeug.security import generate_password_hash
from flask_login import current_user
from functools import wraps
import random
from mailjet_rest import Client
import os
from datetime import datetime, timedelta
import shortuuid
from dash import dcc
from dash import html

# local imports
from CONSTANTS import (
    MAILJET_API_KEY,
    MAILJET_API_SECRET,
    FROM_EMAIL,
    WEBSITE_NAME
)


Column = sqlalchemy.Column
String = sqlalchemy.String
Integer = sqlalchemy.Integer
DateTime = sqlalchemy.DateTime
pwdb = SQLAlchemy()
Column, String, Integer, DateTime = pwdb.Column, pwdb.String, pwdb.Integer, pwdb.DateTime


class User(pwdb.Model):
    id = Column(Integer, primary_key=True)
    first = Column(String(100))
    last = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(100))


def user_table():
    return Table("user", User.metadata)


def add_user(first, last, password, email, engine):
    table = user_table()
    hashed_password = generate_password_hash(password, method="sha256")

    values = dict(first=first, last=last, email=email, password=hashed_password)
    statement = table.insert().values(**values)
    #print("336 - chk user")
    try:
        #print("trying to connect to engine db")
        conn = engine.connect()
        #conn.open()
        print(conn)
        conn.execute(statement)
        #print("after execute")
        conn.close()
        return True
    except:
        #print("337 - connection failed")
        return False


def show_users(engine):
    table = user_table()
    statement = select([table.c.first, table.c.last, table.c.email])

    conn = engine.connect()
    rs = conn.execute(statement)

    for row in rs:
        print(row)

    conn.close()

def del_user(email, engine):
    table = user_table()

    delete = table.delete().where(table.c.email == email)

    conn = engine.connect()
    conn.execute(delete)
    conn.close()

def user_exists(email, engine):
    """
    checks if the user exists with email <email>
    returns
        True if user exists
        False if user exists
    """
    table = user_table()
    statement = table.select().where(table.c.email == email)
    with engine.connect() as conn:
        resp = conn.execute(statement)
        ret = next(filter(lambda x: x.email == email, resp), False)
    return bool(ret)


def change_password(email, password, engine):
    if not user_exists(email, engine):
        return False
    #print("in change pw")
    table = user_table()
    #print("in change pw 1")
    hashed_password = generate_password_hash(password, method="sha256")
    #print("in change pw 2")
    values = dict(password=hashed_password)
    #print("values: ", values)
    #print("in change pw 3")
    #print("table: ", table)
    #print("email: ", email)
    #show_users(engine)
    statement = table.update().where(table.c.email == email).values(values)
    #print("statement: ", statement)
    #print("in change pw 4")

    with engine.connect() as conn:
        conn.execute(statement)
    #print("in change pw 5")
    # success value
    return True

def change_user(first, last, email, engine):
    # if there is no user in the database with that email, return False
    if not user_exists(email, engine):
        return False

    # otherwise, that user exists; update that user's info
    table = user_table()
    values = dict(first=first, last=last,)
    statement = table.update(table).where(table.c.email == email).values(values)
    with engine.connect() as conn:
        conn.execute(statement)
    # success value
    return True


class PasswordChange(pwdb.Model):
    __tablename__ = "password_change"
    id = Column(Integer, primary_key=True)
    email = Column(String(100))
    password_key = Column(String(6))
    timestamp = Column(DateTime())


def password_change_table():
    return Table("password_change", PasswordChange.metadata)


def send_password_key(email, firstname, engine):
    """
    ensure email exists
    create random 6-number password key
    send email with Twilio Sendgrid containing that password key
    return True if that all worked
    return False if one step fails
    """
    print("in send pw key - 0")

    # make sure email exists
    if not user_exists(email, engine):
        print("user does not exist")
        return False

    # generate password key
    key = "".join([random.choice("1234567890") for x in range(6)])

    table = user_table()
    statement = select([table.c.first]).where(table.c.email == email)
    with engine.connect() as conn:
        resp = list(conn.execute(statement))
        if len(resp) == 0:
            return False
        else:
            first = resp[0].first

    # send password key via email
    try:
        print("trying mailjet")
        mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version="v3.1")
        print("001")
        data = {
            "Messages": [
                {
                    "From": {"Email": FROM_EMAIL, "Name": WEBSITE_NAME + "password reset"},
                    "To": [{"Email": email, "Name": first,}],
                    "Subject": "reset password",
                    "TextPart": "anagami password reset code",
                    "HTMLPart": "<p>Dear {},<p> <p>Your anagami password reset code is: <strong>{}</strong> <br>Please enter this code on the website to set a new password.<br><br>Kind regards,<br>Admin".format(
                        firstname, key
                    ),
                    "CustomID": "AppGettingStartedTest",
                }
            ]
        }
        #print("002")
        result = mailjet.send.create(data=data)
        #print("003")
        print(result.status_code, type(result.status_code))
        if int(result.status_code) != 200:
            print("status not 200: ", result.status_code, type(result.status_code))
    except Exception as e:
        #print("exception in sending email")
        traceback.print_exc(e)
        return False

    # store that key in the password_key table
    table = password_change_table()
    #print("004")
    values = dict(email=email, password_key=key, timestamp=datetime.now())
    #print("005")
    statement = table.insert().values(**values)
    #print("006")
    try:
        with engine.connect() as conn:
            conn.execute(statement)
    except:
        return False
    #print("007")
    # change their current password to a random string first, get first and last name
    random_password = "".join([random.choice("1234567890") for x in range(15)])
    #print("008")
    #print("random_password: ", random_password)
    #print("009")
    res = change_password(email, random_password, engine)
    #print("010")
    #print("res: ", res)
    if res:
        return True         # finished successfully
    return False


def validate_password_key(email, key, engine):
    # email exists
    email = email.lower()
    if not user_exists(email, engine):
        return False

    # there is entry matching key and email
    table = password_change_table()
    statement = select([table.c.email, table.c.password_key, table.c.timestamp]).where(
        and_(table.c.email == email, table.c.password_key == key)
    )
    with engine.connect() as conn:
        resp = list(conn.execute(statement))
        if len(resp) == 1:
            if (resp[0].timestamp - (datetime.now() - timedelta(1))).days < 1:
                return True
        return False

    # finished with no erros; return True
    return True
