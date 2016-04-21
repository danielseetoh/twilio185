import psycopg2 as db
import sys

# try:
# con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
print 'Success!'

cur = con.cursor()
        
cur.execute("ALTER TABLE medics ADD COLUMN filename text NOT NULL DEFAULT 'emptyfile'")
cur.execute("ALTER TABLE medics ADD COLUMN filedata bytea NOT NULL DEFAULT 'emptyfile'")
cur.execute("ALTER TABLE medics ADD COLUMN validated bool NOT NULL DEFAULT True")
cur.execute("ALTER TABLE medics ADD COLUMN pending bool NOT NULL DEFAULT False")

con.commit()
con.close()
# except:
#     print 'Failed to connect to database.'