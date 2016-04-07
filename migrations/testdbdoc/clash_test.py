import psycopg2 as db
import sys

con = db.connect(database="testdbdoc", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()
_username = 'asdfdffdfasdf'
_password = 'asdfadf'
_phonenumber = '91230418'
_zipcode = '94720'
cur.execute("INSERT INTO doctors (username, password, phonenumber, zipcode, active) \
            VALUES ('%s', '%s', '%s', '%s', True ) " % (_username, _password, _phonenumber, _zipcode)) 
    
print 'successfully added into database.'

con.commit()
con.close()