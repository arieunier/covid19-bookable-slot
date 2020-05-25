from appsrc import app, db
from flask_migrate import  Migrate
from flask_migrate import MigrateCommand
from flask_script import Manager

#db migrate
#db upgrade

__author__ = 'Augustin Rieunier'

migrate = Migrate(app, db, directory='migrations')

manager =  Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()