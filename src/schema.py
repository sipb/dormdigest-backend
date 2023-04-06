#SQLAlchemy
import sqlalchemy as db
import sqlalchemy.ext.declarative
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import deferred

#Unique ID generation
from auth import random_id_string, random_number_string

import datetime
import creds
import enum

DATABASE_NAME = creds.database_name
SQL_URL = "mysql+mysqlconnector://%s:%s@sql.mit.edu/%s?charset=utf8" % (
    creds.user, creds.password, DATABASE_NAME
)

#Defines length (in characters) of common data types

EMAIL_LENGTH = 64
EMAIL_MESSAGE_ID_LENGTH = 512 #Per RFC-2822 regulation
EVENT_LINK_LENGTH = 512
CLUB_NAME_LENGTH = 128
CLUB_NAME_ABBREV_LENGTH = 32

class UserPrivilege(enum.Enum):
    NORMAL = 0 #Default
    ADMIN = 1
    
class MemberPrivilege(enum.Enum):
    NORMAL = 0 #Default
    OFFICER = 1
    
class EventType(enum.Enum):
    unknown = 0 

##############################################################
# Setup Stages
##############################################################

# Initialization Steps
SQLBase = db.ext.declarative.declarative_base()
sqlengine = db.create_engine(SQL_URL)
SQLBase.metadata.bind = sqlengine
session = db.orm.sessionmaker(bind=sqlengine)()  # main object used for queries

# Main primitives
class Event(SQLBase):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True,
                unique=True, autoincrement=True)

    # User that submitted the event (can be only one!)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    user = relationship("User")
    
    # Event characteristics
    title = Column(String(256))
    club_id = Column(Integer, ForeignKey("clubs.id"))
    club = relationship("Club")
    
    location = Column(String(128), default="")
    description = deferred(Column(Text, default=""))
    description_html = deferred(Column(Text, default=""))

    tags = relationship('EventTag', backref='Event', lazy='dynamic')

    cta_link = Column(String(EVENT_LINK_LENGTH))
    time_start = Column(DateTime,nullable=False)
    time_end = Column(DateTime)

    # Published and approved?
    approved_is = Column(Boolean, default=False)

    date_created = Column(DateTime, default=datetime.datetime.now)
    date_updated = Column(DateTime, default=datetime.datetime.now)

    # Client side
    # type Event = {
    #   start: Date;
    #   end: Date;
    #   title: string;
    #   type: number;
    #   desc: string;
    # };
    def json(self, fullJSON=2):
        additionalJSON = {}
        if (fullJSON == 2):
            additionalJSON = {
                'desc': self.description,
                'desc_html': self.description_html
            }
        elif (fullJSON == 1):
            additionalJSON = {
                'desc': self.description[:100] + "..." if self.description else ""
            }

        return {
            'title': self.title,
            'start': self.time_start.isoformat() + "Z",
            'end': (self.time_end.isoformat() + "Z") if self.time_end else None,
            'location': self.location,
            'link': self.cta_link,
            'approved': self.approved_is,
            'id': self.id,
            **additionalJSON
        }

    def serialize(self):
        return {
            "name": self.title,
            "location": self.location,
            "start_time": self.time_start.isoformat() + "Z",
            "end_time": (self.time_end.isoformat() + "Z") if self.time_end else None,
            "description": self.description_html if self.description_html else self.description,
            "description_text": self.description,
        }

class User(SQLBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True,
                unique=True, autoincrement=True)

    email = Column(String(EMAIL_LENGTH), unique=True, nullable=False)
    user_privilege = Column(Integer, default=0)

    date_created = Column(DateTime, default=datetime.datetime.now)
    date_updated = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, email,user_privilege):
        self.email = email
        self.user_privilege = user_privilege

    def json(self):
        return {
            'email': self.email,
            'user_privilege': self.user_privilege
        }

class Club(SQLBase): 
    __tablename__ = "clubs"
    id = Column(Integer, primary_key=True,
            unique=True, autoincrement=True)
    name = Column(String(CLUB_NAME_LENGTH), unique=True,nullable=False)
    abbrev = Column(String(CLUB_NAME_ABBREV_LENGTH))
    exec_email = Column(String(EMAIL_LENGTH))
    
    def __init__(self, name, abbrev=None, exec_email=None):
        self.name = name
        self.abbrev = abbrev
        self.exec_email = exec_email        

# Relationship Tables
class ClubMembership(SQLBase): #Map user to clubs they are in
    __tablename__ = "club_memberships"
    id = Column(Integer, primary_key=True,
            unique=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)    
    club_id = Column(Integer, ForeignKey("clubs.id"), nullable=False)

class EventTag(SQLBase): #Map event to tags it is associated with
    __tablename__ = "event_tags"
    id = Column(Integer, primary_key=True,
        unique=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"),nullable=False)
    event_tag = Column(Integer, default=0)
    
    def __init__(self, event_id, event_tag):
        self.event_id = event_id
        self.event_tag = event_tag
        
    def get_tag_value(self):
        return self.event_tag

class EventEmail(SQLBase): #Map event email to parsed Event entry
    __tablename__ = "event_emails"
    message_id = Column(String(EMAIL_MESSAGE_ID_LENGTH), primary_key = True, unique=True)
    event_id = Column(Integer, ForeignKey("events.id"),nullable=False)
    event = relationship("Event")

# Implement schema
SQLBase.metadata.create_all(sqlengine)
