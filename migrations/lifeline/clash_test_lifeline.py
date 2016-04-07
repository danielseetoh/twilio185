import psycopg2 as db
import sys

con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()
_username = 'asdfdffdfasdf'
_password = 'asdfadf'
_phonenumber = '91230418'
_zipcode = '94720'
_active = True
cur.execute("INSERT INTO doctors (username, password, phonenumber, zipcode, active) \
            VALUES ('%s', '%s', '%s', '%s', '%r' ) " % (_username, _password, _phonenumber, _zipcode, _active)) 
    
print 'successfully added into database.'

con.commit()
con.close()