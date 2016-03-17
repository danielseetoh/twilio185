import psycopg2 as db
import sys

con = db.connect(database="testdb", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()

cur.execute("SELECT column_name FROM testdb.users.columns WHERE table_name ='table'")
request_fields = cur.fetchall()
print request_fields

con.commit()
con.close()