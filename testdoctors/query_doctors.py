import psycopg2 as db
import sys

con = db.connect(database="testdbdoc", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()
phonenumber = '412341234'
zipcode = '94720'
request_id = '1'
cur.execute("SELECT responded, phonenumber FROM requests WHERE id = '%s' " % (request_id))
responded = cur.fetchall()[0][1]
print responded

# cur.execute("SELECT * FROM doctors WHERE username = 'danielseetoh' and password = 'password123' ")
# request_fields = cur.fetchall()
# if request_fields:
#     print 'logged in'
# else:
#     print 'Wrong username/password'
# numbers = map(str, request_fields)
# for num in request_fields:
#     print num[0]
    


con.commit()
con.close()