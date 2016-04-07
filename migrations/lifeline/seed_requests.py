import psycopg2 as db
import sys

con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()
#set geom
cur.execute("INSERT INTO requests (phonenumber, address, responded, geom) \
VALUES ('+15107100732', (x,y), False, some geom)") 
cur.execute("INSERT INTO requests (phonenumber, address, responded, geom) \
VALUES ('+15107100732', (x,y), False, some geom) ") 
print 'Inserted into table successfully!'

con.commit()
con.close()
