import psycopg2 as db
import sys

con = db.connect(database="testdbdoc", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()

cur.execute("INSERT INTO doctors (username, password, phonenumber, zipcode, active) \
VALUES ('danielseetoh', 'password123', '+15107100732', '94720', True ) ") 
cur.execute("INSERT INTO doctors (username, password, phonenumber, zipcode, active) \
VALUES ('nisha', 'asdf', '+16505578826', '94720', True ) ") 
print 'Inserted into table successfully!'

con.commit()
con.close()
