import sqlalchemy as db
import sqlalchemy.ext.declarative
import sqlalchemy.orm
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

# Implement schema
SQLBase.metadata.create_all(sqlengine)
