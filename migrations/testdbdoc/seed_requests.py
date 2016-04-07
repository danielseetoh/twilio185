import psycopg2 as db
import sys

con = db.connect(database="testdbdoc", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()

cur.execute("INSERT INTO requests (phonenumber, zipcode, responded) \
VALUES ('+15107100732', '94720', False)") 
cur.execute("INSERT INTO requests (phonenumber, zipcode, responded) \
VALUES ('+15107100732', '12345', False) ") 
print 'Inserted into table successfully!'

con.commit()
con.close()
