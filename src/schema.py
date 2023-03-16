#SQLAlchemy
import sqlalchemy as db
import sqlalchemy.ext.declarative
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import deferred

#Email parsing
from emails.parse_type import CATEGORIES

#Unique ID generation
from auth import random_id_string, random_number_string

import datetime
import creds

DATABASE_NAME = creds.database_name
SQL_URL = "mysql+mysqlconnector://%s:%s@sql.mit.edu/%s?charset=utf8" % (
    creds.user, creds.password, DATABASE_NAME
)

##############################################################
# Setup Stages
##############################################################

# Initialization Steps
SQLBase = db.ext.declarative.declarative_base()
sqlengine = db.create_engine(SQL_URL)
SQLBase.metadata.bind = sqlengine
session = db.orm.sessionmaker(bind=sqlengine)()  # main object used for queries

class Event(SQLBase):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True,
                unique=True, autoincrement=True)

    # User that claims the event (can be only one!)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    # Email header information
    header = Column(String(4096), default="") 
    club = Column(String(128), default="")

    # Event characteristics
    title = Column(String(256))
    location = Column(String(128), default="")
    description = deferred(Column(Text, default=""))
    description_html = deferred(Column(Text, default=""))

    cta_link = Column(String(256))
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    etype = Column(Integer, default=0)

    # Published and approved?
    published_is = Column(Boolean, default=False)
    approved_is = Column(Boolean, default=False)

    # Unique event id
    eid = Column(String(10), unique=True)

    # Unique event authstring
    token = Column(String(6))

    date_created = Column(DateTime, default=datetime.datetime.now)
    date_updated = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, user=None):
        self.user = user
        self.generateUniques()

    def generateUniques(self):
        self.eid = random_number_string(10)
        self.token = random_id_string(6)

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
            'end': self.time_end.isoformat() + "Z",
            'location': self.location,
            'type': self.etype,
            'eid': self.eid,
            'link': self.cta_link,
            'approved': self.approved_is,
            'published': self.published_is,
            'header': self.header,
            'parent_id': self.parent_event.eid if self.parent_event_is else '0',
            'id': self.id,
            **additionalJSON
        }

    def serialize(self):
        global CATEGORIES
        cats = []
        for key in CATEGORIES:
            val, _, data = CATEGORIES[key]
            if self.etype & val > 0:
                cats.append(data['name'])
        return {
            "uid": self.eid,
            "name": self.title,
            "location": self.location,
            "start_time": self.time_start.isoformat() + "Z",
            "end_time": self.time_end.isoformat() + "Z",
            "host": "MIT", #TODO(kevinfang): Host not implemented
            "description": self.description_html if self.description_html else self.description,
            "description_text": self.description,
            "categories": "," + ",".join(cats) + ",",
            "sent_from": "Sent by: " + self.header.replace("|", " on ")
        }

class User(SQLBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True,
                unique=True, autoincrement=True)

    email = Column(String(64), unique=True, primary_key=True)

    admin_is = Column(Boolean, default=False)
    
    clients = relationship("Client", back_populates="user")

    date_created = Column(DateTime, default=datetime.datetime.now)
    date_updated = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, email):
        self.email = email

    def json(self):
        return {
            'admin_is': self.admin_is
        }

# Implement schema
SQLBase.metadata.create_all(sqlengine)
