import db.db_operations as db_operations
from db.db_helpers import row2dict
import db.schema as schema
from pprint import pprint

with db_operations.session_scope() as session:

    des_all = session.query(schema.SessionId).order_by(schema.SessionId.date_created).all()
    emails = set()
    for des in des_all:
        emails.add(des.email_addr)
    
    print(emails)
    print("Count:",len(emails))