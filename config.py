import configparser
from sqlalchemy import create_engine
import os

config = configparser.ConfigParser()
config.read('config.txt')

engine = create_engine(config.get('database', 'con'))
#file_path = os.path.abspath(os.getcwd())+"/db/users.db"
#print("file_path: ", file_path)
#engine = create_engine('sqlite:///'+file_path)
#print("engine: ", engine)