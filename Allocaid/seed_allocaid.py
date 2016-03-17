import psycopg2 as db
import sys

con = db.connect(database="testdb", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()

cur.execute("INSERT INTO users (username, password) VALUES ('danielseetoh', 'password123') ") 

print 'Inserted into table successfully!'

con.commit()
con.close()