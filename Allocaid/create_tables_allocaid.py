import psycopg2 as db
import sys

try:
    con = db.connect(database="testdb", user="postgres", password="seetoh", host="localhost")
    print 'Success!'
    
    cur = con.cursor()
    try:
        cur.execute("CREATE TABLE users (username varchar PRIMARY KEY, password varchar);") 
        # still need to add more columns to cover most common items required in disaster
        cur.execute("CREATE TABLE requests (zipcode integer NOT NULL, food integer, water integer);")
        # still need to add tracking for specific requests this fulfilment order has fulfilled
        # possibly don't need this table anymore because we are using distribution centres now
        cur.execute("CREATE TABLE fid (username varchar REFERENCES users (username), fid varchar);") 
        
        print 'Table created successfully!'
    except:
        print 'Failed to create table.'
    con.commit()
    con.close()
except:
    print 'Failed to connect to database.'