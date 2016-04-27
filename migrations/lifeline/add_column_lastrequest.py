import psycopg2 as db
import sys

# try:
# con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
print 'Success!'

cur = con.cursor()
        
cur.execute("ALTER TABLE medics ADD COLUMN lastrequest int")

con.commit()
con.close()
# except:
#     print 'Failed to connect to database.'