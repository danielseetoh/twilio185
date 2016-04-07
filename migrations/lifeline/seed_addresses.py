import psycopg2 as db
import sys

con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()

cur.execute("INSERT INTO addresses (username, password, phonenumber, active) \
VALUES ('danielseetoh', 'password123', '+15107100732', True ) ") 
cur.execute("INSERT INTO addresses (username, password, phonenumber, active) \
VALUES ('nisha', 'asdf', '+16505578826', True ) ") 
print 'Inserted into table successfully!'

con.commit()
con.close()
