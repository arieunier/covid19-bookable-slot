from dataclasses import dataclass
from datetime import datetime
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from appsrc import db
from libs import variables
import uuid
from flask_login import UserMixin


# USER MANAGEMENT PART
from werkzeug.security import generate_password_hash, check_password_hash
class User(UserMixin, db.Model):
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)   


@dataclass
class brand(db.Model):
    # mandatory
    __tablename_ =  "tBrand"
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    name = db.Column(db.String(40), index=True, unique=False, nullable=False)
    website = db.Column(db.String(150), index=True, unique=True, nullable=False)
    company_id = db.Column(db.String(36), db.ForeignKey('tCompany.id'), index=False, nullable=False)
    # optional
    logo_url = db.Column(db.String(150), index=False, unique=False, nullable=True )
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<brand id=%r | name= %r | website= %r | companyid= %r | logourl= %r >' % \
               (self.id, self.name, self.website, self.company_id, self.logo_url)
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'website': self.website,
            'company_id': self.company_id,
            'logo_url': self.logo_url,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN)
        }
        
    @property
    def jsonify(self):
      for entry in self.__dict__:
        print("{} -> {} -> type={}".format(entry, self.__dict__[entry], type(self.__dict__[entry])))


@dataclass
class company(db.Model):
    # mandatory
    __tablename__ =  "tCompany"
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    name = db.Column(db.String(40), index=True, unique=False, nullable=False)
    website = db.Column(db.String(150), index=True, unique=True, nullable=False)
    logo_url = db.Column(db.String(150), index=False, unique=False, nullable=True )

    tax_id = db.Column(db.String(80), index=False, unique=False, nullable=True)
    brands = db.relationship('brand', backref=db.backref('tCompany', lazy='joined'), lazy='dynamic')
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    status = db.Column(db.Integer, index=False, unique=False, nullable=True)

    def __repr__(self):
        return '<company id=%r | name= %r | website= %r | logourl= %r >' % (self.id, self.name, self.website, self.logo_url)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'website': self.website,
            'logo_url': self.logo_url,
            'tax_id' : self.tax_id,
            'brands' : [ item.serialize for item in self.brands ]
        }

#more complex structure related to projects

@dataclass
class RecurringSlotsTemplate(db.Model):
    __tablename__ = "tRecurringSlotsTemplate"
    __jsonName__ = "RecurringSlotsTemplate"
    __curratedValue__  =  [ 
            { 
              'field': 'name', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
            } ,
            { 
              'field': 'slotLength', 
              'isMandatory': True, 
              'forbidenvalues': [''],
              'allowedvalues': [0, 15, 30, 45, 60, 90, 120, 150, 180, 210, 240]
            } , 
            { 
              'field': 'slotCapacity', 
              'isMandatory': True, 
              'forbidenvalues': [0, ''] 
            } ,                        
            { 
              'field': 'description', 
              'isMandatory': False,
              'replaceValue' : '', 
              'forbidenvalues': [ None] 
            }              
          ]
    __unicityCriteria__ = ['name']  
    __unicityCriteriaOr__ = []
    __publicNoLoadOptions__ = []

    # mandatory
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    #fiels  
    name =db.Column(db.String(255), index=False, unique=False, nullable=False )
    description=db.Column(db.String(255), index=False, unique=False, nullable=True )
    slotLength  = db.Column(db.Integer, index=False, unique=False, nullable=False)
    slotCapacity = db.Column(db.Integer, index=False, unique=False, nullable=False)
    # traceability
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<object id={}>'.format(id)

    @property
    def serialize_public(self):
      return self.serialize    
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN),
            'name': self.name,
            'description': self.description,
            'slotCapacity': self.slotCapacity,
            'slotLength': self.slotLength
        }  

class DailySchedule:
  AMOpens  = ''
  AMCloses = ''
  PMOpens = ''
  PMCloses = ''

  def __init__(self, AMOpens='08:00', AMCloses=None, PMOpens=None, PMCloses='20:00'):
    self.AMCloses = AMCloses
    self.AMOpens = AMOpens
    self.PMCloses = PMCloses
    self.PMOpens = PMOpens

  def __repr__(self):
        return self.serialize

  @property
  def serialize_public(self):
    return self.serialize

  @property 
  def serialize(self):
    return self.AMOpens + "/" +  self.AMCloses + "/" + self.PMOpens + "/" + self.PMCloses

@dataclass
class OpeningHoursTemplate(db.Model):
    __tablename__ = "tOpeningHoursTemplate"
    __jsonName__ = "OpeningHoursTemplate"
    __curratedValue__  =  { 
            'name':{ 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
              } ,
           'mon' : {
              'isMandatory': False,
              'replaceValue' : '///', 
              'forbidenvalues': [ None] 
            },   
            'tue': {
              'isMandatory': False,
              'replaceValue' : '///', 
              'forbidenvalues': [ None] 
            },   
            'wed' :  {
              'isMandatory': False,
              'replaceValue' : '///', 
              'forbidenvalues': [ None] 
            },   
            'thu' : {
              'isMandatory': False,
              'replaceValue' : '///', 
              'forbidenvalues': [ None] 
            },   
            'fri' : {
              'isMandatory': False,
              'replaceValue' : '///', 
              'forbidenvalues': [ None] 
            },   
             'sat': { 
              'isMandatory': False,
              'replaceValue' : '///', 
              'forbidenvalues': [ None] 
            },
             'sun': { 
              'isMandatory': False,
              'replaceValue' : '///', 
              'forbidenvalues': [ None] 
            },                           
             'description': {
              'isMandatory': False,
              'replaceValue' : '', 
              'forbidenvalues': [ None] 
            }              
            }
    __unicityCriteria__ = ['name']  
    __unicityCriteriaOr__ = []
    __publicNoLoadOptions__ = []

    # mandatory
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    #fiels  
    name =db.Column(db.String(255), index=False, unique=False, nullable=False )
    description=db.Column(db.String(255), index=False, unique=False, nullable=True )
    # Each configuration must be a json structure of kind
    mon = db.Column(db.String(255), index=False, unique=False, nullable=True, default="///")
    tue = db.Column(db.String(255), index=False, unique=False, nullable=True , default="///")
    wed = db.Column(db.String(255), index=False, unique=False, nullable=True , default="///")
    thu = db.Column(db.String(255), index=False, unique=False, nullable=True , default="///")
    fri = db.Column(db.String(255), index=False, unique=False, nullable=True , default="///")
    sat = db.Column(db.String(255), index=False, unique=False, nullable=True , default="///")
    sun = db.Column(db.String(255), index=False, unique=False, nullable=True , default="///")
    # references
    
    # children
    #openingHoursDetails =  db.relationship('OpeningHoursDetails',  
    #                    primaryjoin="and_(OpeningHoursDetails.refOpeningHoursTemplateId==OpeningHoursTemplate.id)", 
    #                    backref="tOpeningHoursTemplate")

    # traceability
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<object id={}>'.format(id)

    @property
    def serialize_public(self):
      return self.serialize

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'mon': self.mon,
            'tue': self.tue,
            'wed': self.wed,
            'thu':self.thu,
            'fri' : self.fri,
            'sat' : self.sat,
            'sun' : self.sun,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN)
        }                

@dataclass
class Address(db.Model):  
    __tablename__ = "tAddress"
    __jsonName__ = "Address"
    __curratedValue__  = { 
              'street': 
              { 
                'isMandatory': True, 
                'forbidenvalues': [None, ''] 
              } ,
            'number' : 
            {
              'isMandatory': False, 
              'replaceValue' : '', 
              'forbidenvalues': [0, None,''] 
            } ,
            'zipcode':
              {
              'isMandatory': True, 
              'forbidenvalues': [None,''] 
              } , 
            "city" : {
              'isMandatory': True, 
              'forbidenvalues': [None,''] 
             } ,  
             'country': {
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             } ,  
            'state':{
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }             
            }
    __unicityCriteria__ = []  # means an address is not unique
    __unicityCriteriaOr__ = []
    __publicNoLoadOptions__ = []
    # mandatory
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    # fiels
    street = db.Column(db.String(255), index=False, unique=False, nullable=False )
    number = db.Column(db.String(10), index=False, unique=False, nullable=True )
    zipcode = db.Column(db.String(10), index=False, unique=False, nullable=False )
    city= db.Column(db.String(255), index=False, unique=False, nullable=False )
    country = db.Column(db.String(255), index=False, unique=False, nullable=False )
    state = db.Column(db.String(255), index=False, unique=False, nullable=True )
    # references
    # traceability
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<object id={}>'.format(id)
   
    @property
    def serialize_public(self):
      return self.serialize

    @property
    def serialize(self):
        return {
            'id': self.id,
            'street' : self.street,
            'number': self.number,
            'zipcode': self.zipcode,
            'city' : self.city,
            'country': self.country,
            'state':self.state,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN)
        }

@dataclass
class DistributionOwner(db.Model):
    __tablename__ = "tDistributionOwner"
    __jsonName__ = "distributionowner"
    __curratedValue__  =  [ 
            { 
              'field': 'name', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
            } ,
            { 
              'field': 'description', 
              'isMandatory': False, 
              'replaceValue' : '', 
              'forbidenvalues': [] 
            } , 
             { 
              'field': 'logoUrl', 
              'isMandatory': True, 
              'forbidenvalues': [None,''] 
             } , 
            { 
              'field': 'telephone', 
              'isMandatory': True, 
              'forbidenvalues': [None,''] 
             } ,  
            { 
              'field': 'email', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             } ,  
            { 
              'field': 'refAddressId', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             } ,            
          ]
    __unicityCriteria__ = []  # 
    __unicityCriteriaOr__ = ['telephone', 'email'] # unicity is telephone  OR email.
    __publicNoLoadOptions__ = ['distributionPoints']
    # mandatory
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    #fiels  
    name =  db.Column(db.String(255), index=False, unique=False, nullable=False )
    description=db.Column(db.String(255), index=False, unique=False, nullable=True )
    logoUrl=db.Column(db.String(255), index=False, unique=False, nullable=False )
    telephone=db.Column(db.String(255), index=False, unique=True, nullable=False )
    email=db.Column(db.String(255), index=False, unique=True, nullable=False )
    # references & children
    refAddressId = db.Column(db.String(36), db.ForeignKey('tAddress.id'), index=False, nullable=False)
    # children
    address = db.relationship('Address',  
                        primaryjoin="and_(DistributionOwner.refAddressId==Address.id)", 
                        backref="tDistributionOwner")

    distributionPoints =  db.relationship('DistributionPoint',  
                        primaryjoin="and_(DistributionPoint.refDistributionOwnerId==DistributionOwner.id)", 
                        backref="tDistributionOwner")
    
    # traceability
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<object id={}>'.format(id)
   

    @property
    def serialize_public(self):
      return self.serialize

    @property
    def serialize(self):
        return {
            'id': self.id,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN),
            'name' : self.name,
            'description' : self.description,
            'logoUrl' : self.logoUrl,
            'telephone' : self.telephone,
            'email' : self.email,
            'address' : self.address.serialize,
            'distributionPoints' : [ item.serialize for item in self.distributionPoints ]
        }

@dataclass
class DistributionPoint(db.Model):
    __tablename__ = "tDistributionPoint"
    __jsonName__ = "distributionpoint"
    __curratedValue__  =  [ 
            { 
              'field': 'name', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
            } ,
            { 
              'field': 'description', 
              'isMandatory': False, 
              'replaceValue' : '', 
              'forbidenvalues': [] 
            } , 
             { 
              'field': 'logoUrl', 
              'isMandatory': True, 
              'forbidenvalues': [None,''] 
             } , 
            { 
              'field': 'telephone', 
              'isMandatory': True, 
              'forbidenvalues': [None,''] 
             } ,  
            { 
              'field': 'email', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             } ,  
            { 
              'field': 'maxCapacity', 
              'isMandatory': True, 
              'forbidenvalues': [None, 0] 
             } ,              
            { 
              'field': 'refAddressId', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             } ,  
            { 
              'field': 'refDistributionOwnerId', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             } ,   
            { 
              'field': 'refOpeningHoursTemplateId', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'refRecurringSlotsTemplateId', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }                                                
          ]
    __unicityCriteria__ = []  # 
    __unicityCriteriaOr__ = [] # unicity is telephone  OR email.
    __publicNoLoadOptions__ = ['openingHoursTemplate', 'recurringSlotsTemplate']
    # mandatory
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    #fiels  
    name =db.Column(db.String(255), index=False, unique=False, nullable=False )
    description=db.Column(db.String(255), index=False, unique=False, nullable=True )
    logoUrl=db.Column(db.String(255), index=False, unique=False, nullable=False )
    telephone=db.Column(db.String(255), index=False, unique=False, nullable=False )
    email=db.Column(db.String(255), index=False, unique=False, nullable=False )
    maxCapacity=db.Column(db.Integer, index=False, unique=False, nullable=False)
    
    # references & children
    refAddressId = db.Column(db.String(36), db.ForeignKey('tAddress.id'), index=False, nullable=False)
    address = db.relationship('Address',  primaryjoin="and_(DistributionPoint.refAddressId==Address.id)", backref="tDistributionPoint")
    
    refDistributionOwnerId = db.Column(db.String(36), db.ForeignKey('tDistributionOwner.id'), index=False, nullable=False)

    refOpeningHoursTemplateId = db.Column(db.String(36), db.ForeignKey('tOpeningHoursTemplate.id'), index=False, nullable=False)
    openingHoursTemplate = db.relationship('OpeningHoursTemplate',  primaryjoin="and_(DistributionPoint.refOpeningHoursTemplateId==OpeningHoursTemplate.id)", backref="tDistributionPoint")


    refRecurringSlotsTemplateId = db.Column(db.String(36), db.ForeignKey('tRecurringSlotsTemplate.id'), index=False, nullable=False)
    recurringSlotsTemplate = db.relationship('RecurringSlotsTemplate',  primaryjoin="and_(DistributionPoint.refRecurringSlotsTemplateId==RecurringSlotsTemplate.id)", backref="tDistributionPoint")
    # children


    # traceability
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<object id={}>'.format(id)

    @property
    def serialize(self):
      return   {
          'id': self.id,
          'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
          'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN),
          'name' : self.name,
          'description':self.description,
          'logoUrl':self.logoUrl,
          'telephone':self.telephone,
          'email':self.email,
          'maxCapacity':self.maxCapacity,
          'address': self.address.serialize, 
          'refAddressId':  self.refAddressId,
          'refDistributionOwnerId':  self.refDistributionOwnerId,
          'refOpeningHoursTemplate': self.refOpeningHoursTemplateId ,
          'refRecurringSlotsTemplateId':  self.refRecurringSlotsTemplateId   ,            
          'openingHoursTemplate' : self.openingHoursTemplate.serialize,
          'recurringSlotsTemplate': self.recurringSlotsTemplate.serialize
      }

    @property
    def serialize_public(self):
        return  {
            'id': self.id,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN),
            'name' : self.name,
            'description':self.description,
            'logoUrl':self.logoUrl,
            'telephone':self.telephone,
            'email':self.email,
            'maxCapacity':self.maxCapacity,
            'address': self.address.serialize}        
         
@dataclass
class BookableSlot(db.Model):
    __tablename__ = "tBookableSlot"
    __jsonName__ = "bookableslot"
    __curratedValue__  =  [ 
            { 
              'field': 'dateStart', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
            } ,
            { 
              'field': 'dateEnd', 
              'isMandatory': False, 
              'forbidenvalues': [] 
            } , 
             { 
              'field': 'maxCapacity', 
              'isMandatory': True, 
              'forbidenvalues': [0,''] 
             } , 
            { 
              'field': 'refDistributionPoint', 
              'isMandatory': True, 
              'forbidenvalues': [None,''] 
             }                                               
          ]
    __unicityCriteria__ = ['refDistributionPoint', 'dateStart']  # 
    __unicityCriteriaOr__ = [] # 
    __publicNoLoadOptions__ = ['openingHoursTemplate', 'recurringSlotsTemplate']    
    # mandatory
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    # fiels
    dateStart = db.Column(db.DateTime,index=False, unique=False, nullable=False)
    dateEnd = db.Column(db.DateTime,index=False, unique=False, nullable=False)
    maxCapacity = db.Column(db.Integer, index=False, unique=False, nullable=False)
    currentCapacity = db.Column(db.Integer, index=False, unique=False, nullable=False)
    # references
    refDistributionPoint = db.Column(db.String(36), db.ForeignKey('tDistributionPoint.id'), index=False, nullable=False)

    # children

    bookedSlots =  db.relationship('BookedSlot',  
                        primaryjoin="and_(BookedSlot.refBookableSlotId==BookableSlot.id)", 
                        backref="tBookableSlot")

    # traceability
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<object id={}>'.format(id)
   
    @property
    def serialize_public(self):
      return {
            'id': self.id,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN),
            'dateStart' : self.dateStart.strftime(variables.DATETIME_PATTERN),
            'dateEnd' : self.dateEnd.strftime(variables.DATETIME_PATTERN),
            'maxCapacity':self.maxCapacity,
            'currentCapacity':self.currentCapacity,
            'refDistributionPoint':self.refDistributionPoint
        }  

    @property
    def serialize(self):
        return {
            'id': self.id,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN),
            'dateStart' : self.dateStart.strftime(variables.DATETIME_PATTERN),
            'dateEnd' : self.dateEnd.strftime(variables.DATETIME_PATTERN),
            'maxCapacity':self.maxCapacity,
            'currentCapacity':self.currentCapacity,
            'refDistributionPoint':self.refDistributionPoint,
            'bookedSlots': [ item.serialize for item in self.bookedSlots ]
        }        

@dataclass
class BookedSlot(db.Model):
    __tablename__ = "tBookedSlot"
    __jsonName__ = "bookedslots"
    __curratedValue__  =  [ 
            { 
              'field': 'refDistributionPointId', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             } ,   
            { 
              'field': 'refBookableSlotId', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'firstname', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'lastname', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'telephone', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'email', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'numberOfPerson', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }       ,  
            { 
              'field': 'status', 
              'isMandatory': False,
              'replaceValue':'Booked' ,
              'forbidenvalues': [None, ''],
              'allowedvalues': ['Booked', 'checkedIn']
             }                                                                                                                  
          ]
    __unicityCriteria__ = []  # 
    __unicityCriteriaOr__ = [] # unicity is telephone  OR email.
    __publicNoLoadOptions__ = ['openingHoursTemplate', 'recurringSlotsTemplate']
    # mandatory
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    # fiels
    firstname =db.Column(db.String(255), index=False, unique=False, nullable=False )
    lastname =db.Column(db.String(255), index=False, unique=False, nullable=False )
    telephone =db.Column(db.String(255), index=False, unique=False, nullable=False )
    email =db.Column(db.String(255), index=False, unique=False, nullable=False )
    numberOfPerson =db.Column(db.Integer, index=False, unique=False, nullable=False )
    confirmationCode =db.Column(db.String(8), index=False, unique=False, nullable=False )
    status =db.Column(db.String(255), index=False, unique=False, nullable=False )
    # references
    refBookableSlotId = db.Column(db.String(36), db.ForeignKey('tBookableSlot.id'), index=False, nullable=False)
    refDistributionPointId = db.Column(db.String(36), db.ForeignKey('tDistributionPoint.id'), index=False, nullable=False)
    # children
    # traceability
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<object id={}>'.format(id)


    @property
    def serialize_public(self):
        return {
            'id': self.id,
            'firstname' : self.firstname,
            'lastname':self.lastname,
            'telephone':self.telephone,
            'email':self.email,
            'numberOfPerson':self.numberOfPerson,
        }      


    @property
    def serialize(self):
        return {
            'id': self.id,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN),
            'firstname' : self.firstname,
            'lastname':self.lastname,
            'telephone':self.telephone,
            'email':self.email,
            'numberOfPerson':self.numberOfPerson,
            'confirmationCode':self.confirmationCode,
            'status':self.status,
            'refBookableSlot' : self.refBookableSlotId,
            'refDistributionPoint': self.refDistributionPointId
        }      

@dataclass
class CovidTracking(db.Model):
    __tablename__ = "tCovidTracking"
    __jsonName__ = "covidtrackings"
    __curratedValue__  =  [ 
            { 
              'field': 'refDistributionPointId', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             } ,       
            { 
              'field': 'firstname', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'lastname', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'telephone', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'email', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }  ,
            { 
              'field': 'numberOfPerson', 
              'isMandatory': True, 
              'forbidenvalues': [None, ''] 
             }       
             ]     
    __unicityCriteria__ = []  # 
    __unicityCriteriaOr__ = [] # unicity is telephone  OR email.
    __publicNoLoadOptions__ = []
    # mandatory
    id = db.Column(db.String(36), primary_key=True, index=True, unique=True, nullable=False)
    # fiels
    firstname =db.Column(db.String(255), index=False, unique=False, nullable=False )
    lastname =db.Column(db.String(255), index=False, unique=False, nullable=False )
    telephone =db.Column(db.String(255), index=False, unique=False, nullable=False )
    email =db.Column(db.String(255), index=False, unique=False, nullable=False )
    numberOfPerson =db.Column(db.Integer, index=False, unique=False, nullable=False )
    confirmationCode =db.Column(db.String(8), index=False, unique=False, nullable=False )

    # references
    refDistributionPointId = db.Column(db.String(36), db.ForeignKey('tDistributionPoint.id'), index=False, nullable=False)
    # children
    # traceability
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return '<object id={}>'.format(id)


    @property
    def serialize_public(self):
        return {
            'id': self.id,
            'firstname' : self.firstname,
            'lastname':self.lastname,
            'telephone':self.telephone,
            'email':self.email,
            'numberOfPerson':self.numberOfPerson,
        }      


    @property
    def serialize(self):
        return {
            'id': self.id,
            'created_on' : self.created_on.strftime(variables.DATETIME_PATTERN),
            'updated_on' : self.updated_on.strftime(variables.DATETIME_PATTERN),
            'firstname' : self.firstname,
            'lastname':self.lastname,
            'telephone':self.telephone,
            'email':self.email,
            'numberOfPerson':self.numberOfPerson,          
            'refDistributionPoint': self.refDistributionPointId
        }      