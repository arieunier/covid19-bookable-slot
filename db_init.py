from app import app, db
from flask_migrate import  Migrate
from flask_migrate import MigrateCommand
from flask_script import Manager
import  uuid


__author__ = 'Augustin Rieunier'

def purgeDb():
    db.drop_all()
    
def fillDb():
    from app import model
    from model import brand, company

    uid_com_1 = uuid.uuid4().__str__()
    uid_com_2 = uuid.uuid4().__str__()
    companies = [ company(id=uid_com_1,
        name='this is a first name',
        website='www.mywebsite.com'),
        company(id=uid_com_2,
        name='this is a second name',
        website='www.mywebsite2.com')]


    brands = [ brand(id=uuid.uuid4().__str__(), name='brand1', website='www.web1.com',  company_id=uid_com_1),
        brand(id=uuid.uuid4().__str__(), name='brand2', website='www.web2.com',  company_id=uid_com_1), 
        brand(id=uuid.uuid4().__str__(), name='brand3', website='www.web3.com',  company_id=uid_com_1) ]
    
    db.session.add_all(companies)
    db.session.commit()
    
    db.session.add_all(brands)
    db.session.commit()


if __name__ == '__main__':
    purgeDb()
    db.create_all()
    fillDb()