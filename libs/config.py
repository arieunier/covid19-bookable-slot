import os, redis
from libs import variables
basedir = os.path.abspath(os.path.dirname(__file__))

class config(object):
    SQLALCHEMY_DATABASE_URI =  os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY=os.getenv('SECRET_KEY',b"\xf1\xa9'\xb3\xef\xfb]\r\xfff\xe0^\xafk&v")# os.urandom(16))
    APPNAME = os.getenv("APPNAME", "FlaskAPI")
    SESSION_TYPE = os.getenv('SESSION_TYPE','redis')
    SESSION_REDIS = redis.from_url(os.getenv('REDIS_URL',''))

