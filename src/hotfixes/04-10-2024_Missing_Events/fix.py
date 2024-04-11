import sqlite3
from pprint import pprint

con1 = sqlite3.connect("./src/hotfixes/04-10-2024_Missing_Events/prod-dormdigest-prod.db")
con2 = sqlite3.connect("./src/hotfixes/04-10-2024_Missing_Events/xvm-dormdigest-prod.db")

#We want to get back dictionary for easier working
con1.row_factory = sqlite3.Row
con2.row_factory = sqlite3.Row

prod = con1.cursor()
xvm = con2.cursor()

def add_missing_events():
    #print(prod.execute("""SELECT name FROM sqlite_master WHERE type='table';""").fetchall())
    
    #res = prod.execute("SELECT * FROM events WHERE date_created >= date('2024-03-19')").fetchall()
    #pprint([dict(row) for row in res])
    
    # Get all the session IDs from prod
    res = prod.execute("SELECT * FROM session_ids").fetchall()
    dict_res = [dict(row) for row in res]
    print(dict_res[0])
    
    # Delete session IDs from XVM
    res2 = xvm.execute("DELETE FROM session_ids")
    con2.commit()
    
    # Add the session IDs from prod
    for entry in dict_res:
        new_session_id_entry = (entry['session_id'],entry['email_addr'],entry['date_created'])
        res3 = xvm.execute('''INSERT INTO session_ids(session_id,email_addr,date_created) VALUES(?,?,?)''', new_session_id_entry)
    con2.commit()
    
    # Replace all the reference to `dormdigest.xvm.mit.edu` to `dormdigest.mit.edu`
    res4 = xvm.execute("UPDATE event_descriptions SET data = REPLACE(data, 'dormdigest.xvm.mit.edu', 'dormdigest.mit.edu')")
    print(res4)
    con2.commit()

if __name__ == '__main__':
    add_missing_events()